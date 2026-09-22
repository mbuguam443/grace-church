import { Redirect } from 'expo-router';

import { useAuth } from '../lib/auth';

export default function Index() {
  const { booted, token } = useAuth();
  if (!booted) {
    return null;
  }
  return <Redirect href={token ? '/(tabs)' : '/login'} />;
}