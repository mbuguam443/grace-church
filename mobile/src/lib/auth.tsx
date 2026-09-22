import AsyncStorage from '@react-native-async-storage/async-storage';
import React, { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';

import { api, ApiError, STORAGE } from './api';
import { Member, User } from './types';

interface AuthState {
  booted: boolean;
  token: string | null;
  user: User | null;
  member: Member | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
  updateUser: (u: User) => void;
  updateMember: (m: Member | null) => void;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [booted, setBooted] = useState(false);
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [member, setMember] = useState<Member | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const [tok, userRaw, memberRaw] = await Promise.all([
          AsyncStorage.getItem(STORAGE.token),
          AsyncStorage.getItem(STORAGE.user),
          AsyncStorage.getItem(STORAGE.member),
        ]);
        if (tok) {
          setToken(tok);
          if (userRaw) setUser(JSON.parse(userRaw));
          if (memberRaw) setMember(JSON.parse(memberRaw));
          try {
            const me = await api.me(tok);
            setUser(me.user);
            setMember(me.member);
            await AsyncStorage.multiSet([
              [STORAGE.user, JSON.stringify(me.user)],
              [STORAGE.member, JSON.stringify(me.member)],
            ]);
          } catch (e) {
            if (e instanceof ApiError && e.status === 401) {
              setToken(null);
              setUser(null);
              setMember(null);
              await AsyncStorage.multiRemove([STORAGE.token, STORAGE.user, STORAGE.member]);
            }
          }
        }
      } finally {
        setBooted(true);
      }
    })();
  }, []);

  const login = useCallback(async (username: string, password: string) => {
    const res = await api.login(username, password);
    setToken(res.token);
    setUser(res.user);
    setMember(res.member);
    await AsyncStorage.multiSet([
      [STORAGE.token, res.token],
      [STORAGE.user, JSON.stringify(res.user)],
      [STORAGE.member, JSON.stringify(res.member)],
    ]);
  }, []);

  const logout = useCallback(async () => {
    const cur = token;
    setToken(null);
    setUser(null);
    setMember(null);
    await AsyncStorage.multiRemove([STORAGE.token, STORAGE.user, STORAGE.member]);
    if (cur) {
      try {
        await api.logout(cur);
      } catch {
        // ignore network errors on logout
      }
    }
  }, [token]);

  const refresh = useCallback(async () => {
    if (!token) return;
    try {
      const me = await api.me(token);
      setUser(me.user);
      setMember(me.member);
      await AsyncStorage.multiSet([
        [STORAGE.user, JSON.stringify(me.user)],
        [STORAGE.member, JSON.stringify(me.member)],
      ]);
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) {
        await logout();
      }
    }
  }, [token, logout]);

  const updateUser = useCallback((u: User) => setUser(u), []);
  const updateMember = useCallback((m: Member | null) => setMember(m), []);

  const value = useMemo(
    () => ({ booted, token, user, member, login, logout, refresh, updateUser, updateMember }),
    [booted, token, user, member, login, logout, refresh, updateUser, updateMember],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}