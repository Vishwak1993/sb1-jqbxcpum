import React, { useState, useEffect } from 'react';
import { PlusCircle, Loader2, Trash2, Save, AlertCircle, Edit2 } from 'lucide-react';
import { collection, addDoc, query, where, getDocs, deleteDoc, doc, updateDoc, Timestamp, writeBatch } from 'firebase/firestore';
import { db } from '../lib/firebase';
import { useAuth } from '../components/providers/AuthProvider';
import { trackEvent, AnalyticsEvent } from '../utils/analytics';

interface Note {
  id: string;
  title: string;
  content: string;
  userId: string;
  createdAt: Timestamp;
  updatedAt: Timestamp;
}

export const Notes = () => {
  const { user } = useAuth();
  const [notes, setNotes] = useState<Note[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNote, setSelectedNote] = useState<Note | null>(null);
  const [newNote, setNewNote] = useState({ title: '', content: '' });
  const [saving, setSaving] = useState(false);
  const [deleting, setDeleting] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      loadNotes();
    }
  }, [user]);

  const loadNotes = async () => {
    if (!user) return;
    
    setError(null);
    try {
      const notesQuery = query(
        collection(db, 'notes'),
        where('userId', '==', user.uid)
      );
      const snapshot = await getDocs(notesQuery);
      const loadedNotes = snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
      })) as Note[];
      
      setNotes(loadedNotes.sort((a, b) => b.updatedAt.toMillis() - a.updatedAt.toMillis()));
    } catch (error: any) {
      console.error('Error loading notes:', error);
      setError('Failed to load notes. Please try refreshing the page.');
    } finally {
      setLoading(false);
    }
  };

  const createNote = async () => {
    if (!user || !newNote.title.trim()) return;
    
    setSaving(true);
    setError(null);
    try {
      const noteData = {
        title: newNote.title.trim(),
        content: newNote.content.trim(),
        userId: user.uid,
        createdAt: Timestamp.now(),
        updatedAt: Timestamp.now()
      };
      
      const docRef = await addDoc(collection(db, 'notes'), noteData);
      trackEvent(AnalyticsEvent.NOTE_CREATE);
      setNewNote({ title: '', content: '' });
      
      // Update local state instead of reloading
      setNotes(prev => [{
        id: docRef.id,
        ...noteData
      } as Note, ...prev]);
    } catch (error) {
      console.error('Error creating note:', error);
      setError('Failed to create note. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const updateNote = async () => {
    if (!selectedNote || !user) return;
    
    setSaving(true);
    setError(null);
    try {
      const noteRef = doc(db, 'notes', selectedNote.id);
      const updateData = {
        title: selectedNote.title.trim(),
        content: selectedNote.content.trim(),
        updatedAt: Timestamp.now()
      };
      
      await updateDoc(noteRef, updateData);
      trackEvent(AnalyticsEvent.NOTE_EDIT);
      
      // Update local state instead of reloading
      setNotes(prev => prev.map(note => 
        note.id === selectedNote.id 
          ? { ...note, ...updateData }
          : note
      ).sort((a, b) => b.updatedAt.toMillis() - a.updatedAt.toMillis()));
      
      setSelectedNote(null);
    } catch (error) {
      console.error('Error updating note:', error);
      setError('Failed to update note. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const deleteNote = async (noteId: string) => {
    if (!window.confirm('Are you sure you want to delete this note?')) return;
    
    setDeleting(noteId);
    setError(null);
    try {
      // Update local state immediately for better UX
      setNotes(prev => prev.filter(note => note.id !== noteId));
      if (selectedNote?.id === noteId) {
        setSelectedNote(null);
      }

      // Delete in background
      const noteRef = doc(db, 'notes', noteId);
      await deleteDoc(noteRef);
      trackEvent(AnalyticsEvent.NOTE_DELETE);
    } catch (error) {
      console.error('Error deleting note:', error);
      // Restore the note in case of error
      loadNotes();
      setError('Failed to delete note. Please try again.');
    } finally {
      setDeleting(null);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-600" />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-2xl font-bold text-gray-900">My Notes</h1>
        {!selectedNote && (
          <button
            onClick={createNote}
            disabled={saving || !newNote.title.trim()}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
          >
            {saving ? (
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
            ) : (
              <PlusCircle className="h-5 w-5 mr-2" />
            )}
            {saving ? 'Saving...' : 'Save Note'}
          </button>
        )}
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-md flex items-start">
          <AlertCircle className="h-5 w-5 text-red-500 mt-0.5 mr-2 flex-shrink-0" />
          <p className="text-sm text-red-600">{error}</p>
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Note Form */}
        <div className="lg:col-span-2">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <input
              type="text"
              placeholder="Note title"
              value={selectedNote ? selectedNote.title : newNote.title}
              onChange={(e) => selectedNote 
                ? setSelectedNote({...selectedNote, title: e.target.value})
                : setNewNote({...newNote, title: e.target.value})
              }
              className="w-full mb-4 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <textarea
              placeholder="Note content"
              value={selectedNote ? selectedNote.content : newNote.content}
              onChange={(e) => selectedNote
                ? setSelectedNote({...selectedNote, content: e.target.value})
                : setNewNote({...newNote, content: e.target.value})
              }
              rows={8}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <div className="flex justify-end gap-2 mt-4">
              {selectedNote ? (
                <>
                  <button
                    onClick={() => setSelectedNote(null)}
                    className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={updateNote}
                    disabled={saving || !selectedNote.title.trim()}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                  >
                    {saving ? (
                      <Loader2 className="h-4 w-4 animate-spin mr-2" />
                    ) : (
                      <Save className="h-4 w-4 mr-2" />
                    )}
                    {saving ? 'Saving...' : 'Update Note'}
                  </button>
                </>
              ) : (
                <button
                  onClick={createNote}
                  disabled={saving || !newNote.title.trim()}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                >
                  {saving ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : (
                    <PlusCircle className="h-4 w-4 mr-2" />
                  )}
                  {saving ? 'Saving...' : 'Create Note'}
                </button>
              )}
            </div>
          </div>
        </div>

        {/* Notes List */}
        <div className="space-y-4">
          {notes.length === 0 ? (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <p className="text-gray-500 text-sm mb-2">No notes yet</p>
              <p className="text-gray-700">Start by creating your first note!</p>
            </div>
          ) : (
            notes.map(note => (
              <div
                key={note.id}
                className="bg-white p-4 rounded-lg shadow-md hover:shadow-lg transition-shadow"
              >
                <div className="flex justify-between items-start mb-2">
                  <h3 className="text-lg font-medium text-gray-900">
                    {note.title}
                  </h3>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setSelectedNote(note)}
                      className="text-gray-400 hover:text-indigo-600 transition-colors"
                      title="Edit note"
                    >
                      <Edit2 className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => deleteNote(note.id)}
                      disabled={deleting === note.id}
                      className="text-gray-400 hover:text-red-500 disabled:opacity-50 transition-colors"
                      title="Delete note"
                    >
                      {deleting === note.id ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        <Trash2 className="h-4 w-4" />
                      )}
                    </button>
                  </div>
                </div>
                <p className="text-gray-600 text-sm line-clamp-2">
                  {note.content}
                </p>
                <p className="text-xs text-gray-400 mt-2">
                  Last updated: {note.updatedAt.toDate().toLocaleDateString()}
                </p>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};