export interface User {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  full_name: string;
  email: string;
  phone: string;
  role: string;
  role_label: string;
  photo_url: string | null;
}

export interface Member {
  id: number;
  member_number: string;
  first_name: string;
  middle_name: string;
  last_name: string;
  full_name: string;
  gender: string;
  date_of_birth: string | null;
  phone: string;
  email: string;
  address: string;
  photo_url: string | null;
  date_joined: string | null;
  membership_status: string;
  membership_status_label: string;
  membership_type: string;
  membership_type_label: string;
  baptism_status: string;
  baptism_date: string | null;
  salvation_date: string | null;
  marital_status: string;
  occupation: string;
  emergency_contact_name: string;
  emergency_contact_phone: string;
  family: string | null;
}

export interface GivingRecord {
  id: number;
  amount: string;
  category: string;
  category_label: string;
  date: string;
  payment_method: string;
  payment_method_label: string;
  reference_number: string | null;
}

export interface AttendanceRecord {
  id: number;
  service: string;
  date: string;
  start_time: string | null;
  location: string;
  type: string;
  recorded: string;
}

export interface ChurchService {
  id: number;
  name: string;
  date: string;
  start_time: string | null;
  end_time: string | null;
  location: string;
  preacher: string;
  theme: string;
  bible_verse: string;
  checked_in: boolean;
  can_check_in: boolean;
}

export interface Group {
  id: number;
  name: string;
  description: string;
  meeting_day: string;
  meeting_time: string | null;
  location: string;
  leader: string | null;
  members_count: number;
  is_active: boolean;
}

export interface ChurchEvent {
  id: number;
  name: string;
  description: string;
  date: string;
  time: string | null;
  end_date: string | null;
  location: string;
  speaker: string | null;
  capacity: number | null;
  is_full: boolean;
  registrations_count: number;
  registration_required: boolean;
  registered: boolean;
}

export interface Announcement {
  id: number;
  title: string;
  message: string;
  publish_date: string;
  expiry_date: string | null;
  target_audience: string;
}

export interface Sermon {
  id: number;
  title: string;
  speaker: string | null;
  date: string;
  bible_verse: string | null;
  series: string | null;
  category: string | null;
  description: string | null;
  youtube_url: string | null;
  has_audio?: boolean;
  has_video?: boolean;
  has_pdf?: boolean;
  sermon_notes?: string | null;
  pdf_url?: string | null;
  audio_url?: string | null;
  video_url?: string | null;
}

export interface BibleStudyNote {
  id: number;
  title: string;
  bible_verse: string;
  study_date: string;
  teacher: string | null;
  series: string | null;
  content?: string;
  key_points?: string;
  prayer_points?: string;
  discussion_questions?: string;
}

export interface Song {
  id: number;
  title: string;
  category: string;
  category_label: string;
  author: string | null;
  scripture: string | null;
  key: string | null;
  tempo: string | null;
  youtube_url: string | null;
  lyrics?: string;
}

export interface Prayer {
  id: number;
  title: string;
  request: string;
  category: string;
  category_label: string;
  date: string;
  status: string;
  status_label: string;
  is_confidential: boolean;
  is_mine: boolean;
}

export interface AppNotification {
  id: number;
  title: string;
  message: string;
  kind: string;
  is_read: boolean;
  created_at: string;
}

export interface NotificationsResponse {
  results: AppNotification[];
  count: number;
  unread_count: number;
}

export interface PortalCounts {
  groups: number;
  givings: number;
  givings_total: string;
  attendance: number;
  events: number;
  announcements: number;
}

export interface PortalData {
  member: Member | null;
  unread_count?: number;
  counts: PortalCounts;
  groups: Group[];
  givings: GivingRecord[];
  attendance: AttendanceRecord[];
  events: ChurchEvent[];
  announcements: Announcement[];
  today_services: ChurchService[];
}

export interface LoginResponse {
  token: string;
  user: User;
  member: Member | null;
}

export interface ListResponse<T> {
  results: T[];
  count: number;
  total?: string;
}
export interface CourseEnrollment {
  id: number;
  status: string;
  status_label: string;
  is_child: boolean;
  student_name: string;
  parent_name: string;
  joined_at: string;
}

export interface SundaySchoolCourse {
  id: number;
  title: string;
  age_group: string;
  age_group_label: string;
  lesson_date: string | null;
  scripture: string;
  video_url: string;
  enrolled_count: number;
  pending_count: number;
  max_students: number | null;
  spots_left: number | null;
  is_full: boolean;
  enable_registration: boolean;
  requires_approval: boolean;
  can_join: boolean;
  can_view_content: boolean;
  my_enrollment: CourseEnrollment | null;
  memory_verse?: string;
  lesson?: string;
  activities?: string;
  updated_at?: string;
  pdf_url?: string | null;
  audio_url?: string | null;
  video_file_url?: string | null;
  my_children_on_course?: string[];
}

export interface CourseComment {
  id: number;
  body: string;
  author: string;
  created_at: string;
  is_mine: boolean;
  can_delete: boolean;
  attachment_url: string | null;
}

export interface ChildClassSummary {
  id: number;
  title: string;
  status: string;
  status_label: string;
  age_group_label: string;
}

export interface Child {
  id: number;
  first_name: string;
  last_name: string;
  full_name: string;
  date_of_birth: string;
  age: number;
  age_group: string;
  age_group_label: string;
  gender: string;
  school_class: string;
  teacher: string;
  allergies: string;
  emergency_contact: string;
  photo_url: string | null;
  is_active: boolean;
  checked_in_today: boolean;
  checked_out_today: boolean;
  checkin_time: string | null;
  classes: ChildClassSummary[];
}

export interface DirectoryMember {
  id: number;
  full_name: string;
  first_name: string;
  last_name: string;
  member_number: string;
  phone: string;
  email: string;
  gender: string;
  membership_status: string;
  membership_status_label: string;
  photo_url: string | null;
  family?: string | null;
}

export interface Ministry {
  id: number;
  name: string;
  description: string;
  leader: string | null;
  purpose: string;
  image_url: string | null;
  members?: DirectoryMember[];
}

export interface GroupDetail extends Group {
  members: { id: number; full_name: string; phone: string; email: string }[];
}

export interface Facility {
  id: number;
  name: string;
  description: string;
  capacity: number;
  location: string;
  is_available: boolean;
}

export interface FacilityBooking {
  id: number;
  facility: string;
  event_name: string;
  date: string;
  start_time: string;
  end_time: string;
  purpose: string;
  status: string;
  status_label: string;
}

export interface OnlineGiving {
  id: number;
  name: string;
  email: string;
  amount: string;
  giving_category: string;
  giving_category_label: string;
  frequency: string;
  frequency_label: string;
  reference_number: string;
  status: string;
  status_label: string;
  created_at: string;
}

export interface SundaySchoolDetailResponse {
  course: SundaySchoolCourse;
  comments: CourseComment[];
}