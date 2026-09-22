import { DefaultTheme, Stack, ThemeProvider } from 'expo-router';
import * as SplashScreen from 'expo-splash-screen';
import { useEffect } from 'react';
import { ActivityIndicator, Image, StyleSheet, Text, View } from 'react-native';

import { AuthProvider, useAuth } from '../lib/auth';
import { Colors } from '../lib/theme';

SplashScreen.preventAutoHideAsync();

function BootScreen() {
  return (
    <View style={styles.boot}>
      <Image source={require('../../assets/images/gc-logo.png')} style={styles.bootLogo} resizeMode="contain" />
      <Text style={styles.bootName}>Grace Church Munyaka</Text>
      <ActivityIndicator color={Colors.navy} style={styles.bootSpinner} />
    </View>
  );
}

function RootNavigator() {
  const { booted } = useAuth();

  useEffect(() => {
    SplashScreen.hideAsync();
  }, []);

  if (!booted) {
    return <BootScreen />;
  }

  const navTheme = {
    ...DefaultTheme,
    colors: {
      ...DefaultTheme.colors,
      primary: Colors.navy,
      background: Colors.bg,
      card: Colors.card,
      text: Colors.text,
      border: Colors.border,
    },
  };

  return (
    <ThemeProvider value={navTheme}>
      <Stack
        screenOptions={{
          headerTintColor: Colors.navy,
          headerTitleStyle: { fontWeight: '800' },
          headerStyle: { backgroundColor: Colors.card },
          contentStyle: { backgroundColor: Colors.bg },
        }}>
        <Stack.Screen name="index" options={{ headerShown: false }} />
        <Stack.Screen name="login" options={{ headerShown: false }} />
        <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
        <Stack.Screen name="list/[kind]" options={{ title: 'Records' }} />
        <Stack.Screen name="read/[kind]/[id]" options={{ title: 'Notes' }} />
        <Stack.Screen
          name="prayers/new"
          options={{ title: 'New Prayer Request', presentation: 'modal', headerBackButtonDisplayMode: 'minimal' }}
        />
        <Stack.Screen name="notifications" options={{ title: 'Updates' }} />
      </Stack>
    </ThemeProvider>
  );
}

export default function RootLayout() {
  return (
    <AuthProvider>
      <RootNavigator />
    </AuthProvider>
  );
}

const styles = StyleSheet.create({
  boot: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFFFF',
    padding: 32,
  },
  bootLogo: {
    width: 240,
    height: 240,
  },
  bootName: {
    marginTop: 20,
    fontSize: 16,
    fontWeight: '700',
    color: Colors.navy,
    textAlign: 'center',
  },
  bootSpinner: {
    marginTop: 24,
  },
});