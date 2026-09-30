import Constants, { ExecutionEnvironment } from 'expo-constants';
import * as Notifications from 'expo-notifications';
import { Platform } from 'react-native';

import { api } from './api';

let handlerReady = false;

/**
 * Set once, lazily, and never at module scope.
 *
 * expo-notifications throws as soon as it is used in Expo Go on Android, where
 * remote push was removed in SDK 53. Doing this at import time took the whole
 * screen down with it, so every call has to be guarded and deferred.
 */
function ensureHandler() {
  if (handlerReady) return;
  handlerReady = true;
  try {
    Notifications.setNotificationHandler({
      handleNotification: async () => ({
        shouldShowBanner: true,
        shouldShowList: true,
        shouldPlaySound: true,
        shouldSetBadge: false,
      }),
    });
  } catch {
    // Not supported here; local notifications simply stay off.
  }
}

/** Remote push needs a development build on Android. Local notifications are fine in Expo Go. */
export function remotePushSupported(): boolean {
  if (Platform.OS !== 'android') return true;
  return Constants.executionEnvironment !== ExecutionEnvironment.StoreClient;
}

export async function setupNotificationChannel() {
  ensureHandler();
  if (Platform.OS === 'android') {
    try {
      await Notifications.setNotificationChannelAsync('updates', {
        name: 'Updates',
        importance: Notifications.AndroidImportance.HIGH,
        vibrationPattern: [0, 250, 250, 250],
      });
    } catch {
      // channel setup may be unavailable in some environments
    }
  }
}

export async function registerPushToken(token: string) {
  if (!remotePushSupported()) return;
  ensureHandler();
  try {
    const projectId = Constants.expoConfig?.extra?.eas?.projectId ?? Constants.easConfig?.projectId;
    if (!projectId) return;
    const { status } = await Notifications.getPermissionsAsync();
    if (status !== 'granted') return;
    const pushToken = (await Notifications.getExpoPushTokenAsync({ projectId })).data;
    await api.registerDevice(token, pushToken, Platform.OS);
  } catch {
    // remote push needs a development build; ignore in Expo Go
  }
}

export async function presentLocalNotification(title: string, body: string) {
  ensureHandler();
  try {
    await Notifications.scheduleNotificationAsync({
      content: { title, body, sound: 'default' },
      trigger: null,
    });
  } catch {
    // notifications may be unavailable (web/simulator without permission)
  }
}

export async function requestNotificationPermission() {
  ensureHandler();
  try {
    const { status } = await Notifications.requestPermissionsAsync();
    return status === 'granted';
  } catch {
    return false;
  }
}
