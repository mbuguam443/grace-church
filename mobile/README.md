# GC Members — Mobile App

Expo (React Native) members portal for Grace Church Munyaka (GC), powered by the Django
backend's JSON API (`/api/`). Built with **Expo Go** in mind — no native build required.

## Features

- Sign in with the same username/password used on the church website.
- **My Portal** — dashboard with giving total, attendance, groups and upcoming events.
- **Library** — browse groups, giving history, attendance, upcoming events, announcements,
  sermons (with YouTube links) and your prayer requests.
- **Events** — register for / cancel event registration right from the app.
- **Prayer requests** — submit new requests, choose a category, mark confidential.
- **Profile** — view your member record, edit contact details, change photo, change password.

## Tech notes

- Expo SDK 57, expo-router v6 (file-based routing), TypeScript.
- Only Expo Go-compatible packages: `@expo/vector-icons`, `@react-native-async-storage/async-storage`,
  `expo-image`, `expo-image-picker`, `expo-web-browser`.
- Auth via a bearer token stored in AsyncStorage. Backend endpoint: `POST /api/login/`.

## Run it

1. Install the **Expo Go** app on your phone (App Store / Google Play).
2. Start the dev server:

   ```sh
   cd mobile
   npm install
   npx expo start
   ```

3. Scan the QR code with the Expo Go app (same Wi-Fi network as your computer).

The app points at the live site (`https://gc.schones-heim-builders.co.ke`). The API base URL is
fixed in `src/lib/api.ts` (`DEFAULT_SERVER_URL`) so members never see it. To test against a local
Django server, change that constant and reload, e.g. `http://<your-computer-LAN-IP>:8000`
(use the LAN IP, not `127.0.0.1`).

## Backend API

The Django project this app talks to lives one folder up. It exposes:

```
POST /api/login/            GET  /api/portal/
POST /api/logout/           GET  /api/me/
GET/POST /api/profile/      POST /api/profile/password/
GET /api/groups/            GET  /api/givings/
GET /api/attendance/        GET  /api/events/
POST /api/events/<id>/register/
GET /api/announcements/     GET  /api/sermons/
GET/POST /api/prayers/
```

Auth header: `Authorization: Token <key>`. After backend changes, deploy on the server
(see `../update.py`) then refresh the app.

## Commands

```sh
npx expo start        # dev server + QR code
npx expo export       # production bundle (verifies the app compiles)
npx tsc --noEmit      # type check
npx expo lint         # lint
npm run reset-project # scaffold empty project (template convenience)
```