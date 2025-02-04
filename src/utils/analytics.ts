import { analytics } from '../lib/firebase';
import { logEvent } from 'firebase/analytics';

export enum AnalyticsEvent {
  PAGE_VIEW = 'page_view',
  SIGN_UP = 'sign_up',
  LOGIN = 'login',
  LOGOUT = 'logout',
  NOTE_CREATE = 'note_create',
  NOTE_EDIT = 'note_edit',
  NOTE_DELETE = 'note_delete',
  SEARCH = 'search'
}

export const trackEvent = (eventName: AnalyticsEvent, params?: Record<string, any>) => {
  if (analytics) {
    logEvent(analytics, eventName, params);
  }
};

export const trackPageView = (path: string) => {
  trackEvent(AnalyticsEvent.PAGE_VIEW, { page_path: path });
};