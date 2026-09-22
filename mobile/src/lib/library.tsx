export type ModuleKind =
  | 'groups'
  | 'givings'
  | 'attendance'
  | 'events'
  | 'announcements'
  | 'sermons'
  | 'bible-study'
  | 'devotions'
  | 'songs'
  | 'prayers';

export interface ModuleMeta {
  kind: ModuleKind;
  title: string;
  subtitle: string;
  icon: string;
}

export const MODULES: ModuleMeta[] = [
  { kind: 'groups', title: 'My Groups', subtitle: 'Fellowships & departments', icon: 'people' },
  { kind: 'givings', title: 'Giving History', subtitle: 'Offerings, tithes & pledges', icon: 'wallet' },
  { kind: 'attendance', title: 'Attendance', subtitle: 'Services you have attended', icon: 'calendar' },
  { kind: 'events', title: 'Events', subtitle: 'Upcoming church events', icon: 'megaphone' },
  { kind: 'announcements', title: 'Announcements', subtitle: 'Latest church notices', icon: 'checkbox' },
  { kind: 'sermons', title: 'Sermons', subtitle: 'Messages, notes & videos', icon: 'mic' },
  { kind: 'bible-study', title: 'Bible Study', subtitle: 'Study notes & key points', icon: 'book' },
  { kind: 'devotions', title: 'Devotions', subtitle: 'Daily devotion messages', icon: 'sunny' },
  { kind: 'songs', title: 'Songs & Hymns', subtitle: 'Lyrics & worship songs', icon: 'musical-notes' },
  { kind: 'prayers', title: 'Prayer Requests', subtitle: 'Share and track your prayer needs', icon: 'hand-left' },
];

export function moduleTitle(kind: string): string {
  const m = MODULES.find((x) => x.kind === kind);
  return m ? m.title : 'Records';
}

export const PRAYER_CATEGORIES = [
  { value: 'health', label: 'Health' },
  { value: 'family', label: 'Family' },
  { value: 'finances', label: 'Finances' },
  { value: 'spiritual', label: 'Spiritual growth' },
  { value: 'guidance', label: 'Guidance' },
  { value: 'thanksgiving', label: 'Thanksgiving' },
  { value: 'other', label: 'Other' },
];