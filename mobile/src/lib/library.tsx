export type ModuleKind =
  | 'groups'
  | 'groups-all'
  | 'givings'
  | 'attendance'
  | 'events'
  | 'announcements'
  | 'sermons'
  | 'bible-study'
  | 'sunday-school'
  | 'devotions'
  | 'songs'
  | 'prayers'
  | 'children'
  | 'ministries'
  | 'facilities'
  | 'my-bookings'
  | 'directory'
  | 'online-giving';

export interface ModuleMeta {
  kind: ModuleKind;
  title: string;
  subtitle: string;
  icon: string;
}

export const MODULES: ModuleMeta[] = [
  { kind: 'sunday-school', title: 'Sunday School', subtitle: 'Classes & lessons for your children', icon: 'school' },
  { kind: 'children', title: 'My Children', subtitle: 'Check in, out & view classes', icon: 'happy' },
  { kind: 'bible-study', title: 'Bible Study', subtitle: 'Study notes & key points', icon: 'book' },
  { kind: 'sermons', title: 'Sermons', subtitle: 'Messages, notes & videos', icon: 'mic' },
  { kind: 'devotions', title: 'Devotions', subtitle: 'Daily devotion messages', icon: 'sunny' },
  { kind: 'songs', title: 'Songs & Hymns', subtitle: 'Lyrics & worship songs', icon: 'musical-notes' },
  { kind: 'groups', title: 'My Groups', subtitle: 'Fellowships & departments', icon: 'people' },
  { kind: 'groups-all', title: 'All Groups', subtitle: 'Find a fellowship to join', icon: 'people-circle' },
  { kind: 'ministries', title: 'Ministries', subtitle: 'Serve in a department', icon: 'hand-left' },
  { kind: 'prayers', title: 'Prayer Requests', subtitle: 'Share and track your prayer needs', icon: 'chatbubbles' },
  { kind: 'givings', title: 'Giving History', subtitle: 'Offerings, tithes & pledges', icon: 'wallet' },
  { kind: 'online-giving', title: 'Give', subtitle: 'Send an offering or tithe', icon: 'card' },
  { kind: 'attendance', title: 'Attendance', subtitle: 'Services you have attended', icon: 'calendar' },
  { kind: 'events', title: 'Events', subtitle: 'Upcoming church events', icon: 'megaphone' },
  { kind: 'announcements', title: 'Announcements', subtitle: 'Latest church notices', icon: 'checkbox' },
  { kind: 'facilities', title: 'Facilities', subtitle: 'Book a hall or room', icon: 'business' },
  { kind: 'my-bookings', title: 'My Bookings', subtitle: 'Requests you have made', icon: 'calendar-number' },
  { kind: 'directory', title: 'Members', subtitle: 'Contact details & phone book', icon: 'call' },
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