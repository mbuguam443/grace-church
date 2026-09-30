# GC Members — Mobile App

Expo (React Native) members portal for Grace Church Munyaka (GC), powered by the Django
backend's JSON API (`/api/`). Built with **Expo Go** in mind — no native build required.

## Features

- Sign in with the same username/password used on the church website.
- **My Portal** — dashboard with giving total, attendance, groups, upcoming events, service
  check-in, plus shortcuts to Give and the member directory.
- **Library** — grouped into The Word, My church family, Worship, My records and Church life.
- **Sunday School** — browse classes, join/leave (parents enrol their own children), read the
  lesson, memory verse, activities, PDF/audio/video, and join the class discussion.
- **My Children** — each child's age group, Sunday School class, details, and one-tap
  check-in / check-out.
- **Bible Study** — study notes, key points, prayer points, discussion questions, join/leave the
  study, and post or read discussion comments.
- **Give** — submit a tithe, offering or project contribution as one-time, monthly or annual,
  with your giving history.
- **Groups** — your own groups plus a browsable directory of every active group, with leader,
  meeting time and member roster.
- **Ministries** — what each department does, its leader and its team members.
- **Facilities** — browse bookable facilities and submit booking requests; see the status of
  each request under My Bookings.
- **Members** — searchable member directory with phone/email (home addresses and emergency
  contacts are never exposed).
- **Events** — register for / cancel event registration, with start and end times.
- **Prayer requests** — submit new requests, choose a category, mark confidential.
- **Sermons, devotionals, songs** — read notes, lyrics, YouTube and PDF links.
- **Updates** — a bell with an unread count on the portal, and a notifications screen. Both read
  `GET /api/notifications/`, so updates work with no push setup. When new items arrive while the app
  is open, a banner appears at the top of the portal; tap it to read them.
- **Profile** — view your member record, edit contact details, change photo, change password.

## Tech notes

- Expo SDK 57, expo-router v6 (file-based routing), TypeScript.
- Only Expo Go-compatible packages: `@expo/vector-icons`, `@react-native-async-storage/async-storage`,
  `expo-image`, `expo-image-picker`, `expo-web-browser`.
- Auth via a bearer token stored in AsyncStorage. Backend endpoint: `POST /api/login/`.
- No `expo-notifications`. Remote push was removed from Expo Go on Android in SDK 53 and does not
  work there, so it was removed rather than left throwing on every launch. Member updates are
  delivered in-app from `GET /api/notifications/` instead. If push is ever wanted it needs a
  development build (`eas build`, or `npx expo run:android`) plus an `extra.eas.projectId` in
  `app.json`, neither of which is set up.

## Run it

1. Install the **Expo Go** app on your phone (App Store / Google Play).
2. Start the dev server:

   ```sh
   cd mobile
   npm install
   npx expo start
   ```

3. Scan the QR code with the Expo Go app (same Wi-Fi network as your computer).

The app points at the live Grace Church Munyaka site (`https://gracechurch.schones-heim-builders.co.ke`).
The API base URL is fixed in `src/lib/api.ts` (`DEFAULT_SERVER_URL`) so members never see it. To
test against a local Django server, change that constant and reload, e.g.
`http://<your-computer-LAN-IP>:8000` (use the LAN IP, not `127.0.0.1`).

Note: `fbmi.schones-heim-builders.co.ke` is a **different** church (Fruitful Brethren Ministry
International) on the same host, and `gc.schones-heim-builders.co.ke` does not resolve. Do not point
this app at either of them.

## Backend API

The Django project this app talks to lives one folder up. It exposes:

```
POST /api/login/               GET  /api/portal/
POST /api/logout/              GET  /api/me/
GET/POST /api/profile/         POST /api/profile/password/
GET  /api/groups/              GET  /api/groups/browse/
GET  /api/groups/<id>/         GET  /api/givings/
GET  /api/attendance/          GET  /api/events/
GET  /api/events/<id>/         POST /api/events/<id>/register/
GET  /api/services/<id>/       POST /api/services/<id>/attend/
GET  /api/announcements/       GET  /api/sermons/
GET/POST /api/prayers/         GET  /api/bible-study/
POST /api/bible-study/<id>/join/   /leave/   /comments/
GET  /api/sunday-school/       GET  /api/sunday-school/<id>/
POST /api/sunday-school/<id>/join/  /leave/  /comments/
GET  /api/children/            POST /api/children/<id>/checkin/  /checkout/
GET/POST /api/give/            GET  /api/members/
GET  /api/members/<id>/        GET  /api/ministries/
GET  /api/ministries/<id>/     GET/POST /api/facilities/
GET  /api/facilities/bookings/
GET  /api/devotions/           GET  /api/songs/
GET  /api/notifications/        POST /api/devices/
```

List endpoints accept `?search=` and return `{ results: [...], count: n }`. Auth header:
`Authorization: Token <key>`. After backend changes, deploy on the server (see `../update.py`)
then refresh the app.

## Commands

```sh
npx expo start        # dev server + QR code
npx expo export       # production bundle (verifies the app compiles)
npx tsc --noEmit      # type check
npx expo lint         # lint
npm run reset-project # scaffold empty project (template convenience)
```