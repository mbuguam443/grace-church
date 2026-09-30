import { Ionicons } from '@expo/vector-icons';
import { Stack, router } from 'expo-router';
import { useEffect, useState } from 'react';
import { KeyboardAvoidingView, Platform, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { Btn, Card, ErrorBox, Field, Loading } from '../../components/ui';
import { useAuth } from '../../lib/auth';
import { api } from '../../lib/api';
import { Colors, formatDate, Radius, Spacing } from '../../lib/theme';
import { Facility } from '../../lib/types';

const TIME_RE = /^([01]\d|2[0-3]):[0-5]\d$/;

function todayIso(): string {
  const now = new Date();
  const month = `${now.getMonth() + 1}`.padStart(2, '0');
  const day = `${now.getDate()}`.padStart(2, '0');
  return `${now.getFullYear()}-${month}-${day}`;
}

export default function NewBookingScreen() {
  const { token } = useAuth();
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [facility, setFacility] = useState<number | null>(null);
  const [eventName, setEventName] = useState('');
  const [date, setDate] = useState(todayIso());
  const [startTime, setStartTime] = useState('09:00');
  const [endTime, setEndTime] = useState('11:00');
  const [purpose, setPurpose] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) return;
    (async () => {
      try {
        const res = await api.list<Facility>(token, 'facilities/');
        setFacilities(res.results ?? []);
        setLoadError(null);
      } catch (e) {
        setLoadError(e instanceof Error ? e.message : 'Could not load the facilities.');
      } finally {
        setLoading(false);
      }
    })();
  }, [token]);

  const validation = (() => {
    if (!facility) return 'Choose a facility.';
    if (!eventName.trim()) return 'Give the booking a name.';
    if (!/^\d{4}-\d{2}-\d{2}$/.test(date.trim())) return 'Use the format YYYY-MM-DD for the date.';
    if (!TIME_RE.test(startTime.trim())) return 'Use the format HH:MM for the start time.';
    if (!TIME_RE.test(endTime.trim())) return 'Use the format HH:MM for the end time.';
    if (endTime.trim() <= startTime.trim()) return 'The end time must be after the start time.';
    return null;
  })();

  async function submit() {
    if (!token || validation) return;
    setBusy(true);
    setError(null);
    try {
      await api.createBooking(token, {
        facility: facility!,
        event_name: eventName.trim(),
        date: date.trim(),
        start_time: startTime.trim(),
        end_time: endTime.trim(),
        purpose: purpose.trim(),
      });
      router.replace('/list/my-bookings');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not make this booking.');
    } finally {
      setBusy(false);
    }
  }

  return (
    <View style={styles.safe}>
      <Stack.Screen options={{ title: 'Book a facility', headerShadowVisible: false }} />
      <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : undefined} style={styles.flex}>
        <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">
          <View style={styles.hero}>
            <Ionicons name="business-outline" size={18} color={Colors.gold} />
            <Text style={styles.heroTitle}>Request a booking</Text>
            <Text style={styles.heroSub}>Bookings are reviewed by the church office before they are approved.</Text>
            <View style={styles.goldBar} />
          </View>

          <View style={styles.body}>
            {loadError ? <ErrorBox text={loadError} /> : null}

            <View style={styles.group}>
              <Text style={styles.groupLabel}>Facility</Text>
              {loading ? (
                <Loading />
              ) : facilities.length === 0 ? (
                <Card>
                  <Text style={styles.sub}>No facilities are available for booking right now.</Text>
                </Card>
              ) : (
                facilities.map((f) => {
                  const active = facility === f.id;
                  return (
                    <Pressable key={f.id} onPress={() => setFacility(f.id)} style={[styles.option, active && styles.optionActive]}>
                      <View style={styles.optionText}>
                        <Text style={styles.optionLabel}>{f.name}</Text>
                        <Text style={styles.optionHint}>
                          {[f.location, f.capacity ? `Seats ${f.capacity}` : null].filter(Boolean).join(' · ') || 'Available to book'}
                        </Text>
                      </View>
                      <Ionicons
                        name={active ? 'radio-button-on' : 'radio-button-off'}
                        size={20}
                        color={active ? Colors.gold : Colors.border}
                      />
                    </Pressable>
                  );
                })
              )}
            </View>

            <Field
              label="What is the booking for?"
              value={eventName}
              onChangeText={setEventName}
              placeholder="e.g. Youth team meeting"
            />

            <View style={styles.row}>
              <View style={styles.rowItem}>
                <Field
                  label="Date (YYYY-MM-DD)"
                  value={date}
                  onChangeText={setDate}
                  placeholder="2026-01-31"
                  autoCapitalize="none"
                  style={styles.compact}
                />
                {date.length === 10 && /^\d{4}-\d{2}-\d{2}$/.test(date) ? (
                  <Text style={styles.hint}>{formatDate(date)}</Text>
                ) : null}
              </View>
            </View>

            <View style={styles.row}>
              <View style={styles.rowItem}>
                <Field label="Start (HH:MM)" value={startTime} onChangeText={setStartTime} placeholder="09:00" autoCapitalize="none" />
              </View>
              <View style={styles.rowItem}>
                <Field label="End (HH:MM)" value={endTime} onChangeText={setEndTime} placeholder="11:00" autoCapitalize="none" />
              </View>
            </View>

            <Field
              label="Purpose or notes (optional)"
              value={purpose}
              onChangeText={setPurpose}
              placeholder="Anything we should know"
              multiline
              style={styles.notes}
            />

            {validation ? <Text style={styles.error}>{validation}</Text> : null}
            {error ? <Text style={styles.error}>{error}</Text> : null}

            <Btn title="Submit booking request" loading={busy} disabled={!!validation} onPress={submit} />
          </View>
        </ScrollView>
      </KeyboardAvoidingView>
    </View>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  flex: { flex: 1 },
  scroll: { paddingBottom: Spacing.xl },
  hero: { backgroundColor: Colors.navy, paddingHorizontal: Spacing.lg, paddingVertical: Spacing.xl, gap: Spacing.sm },
  heroTitle: { fontSize: 22, fontWeight: '900', color: '#FFF' },
  heroSub: { fontSize: 13, color: 'rgba(255,255,255,0.8)', lineHeight: 19 },
  goldBar: { marginTop: Spacing.sm, height: 3, width: 56, borderRadius: 999, backgroundColor: Colors.gold },
  body: { padding: Spacing.lg, gap: Spacing.lg },
  group: { gap: Spacing.sm },
  groupLabel: { fontSize: 12, fontWeight: '800', color: Colors.muted, textTransform: 'uppercase', letterSpacing: 0.4 },
  option: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: Spacing.md,
    backgroundColor: Colors.card,
    borderRadius: Radius.md,
    padding: Spacing.md,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: Colors.border,
  },
  optionActive: { borderColor: Colors.gold, backgroundColor: Colors.goldLight },
  optionText: { flex: 1, gap: 2 },
  optionLabel: { fontSize: 15, fontWeight: '700', color: Colors.text },
  optionHint: { fontSize: 12, color: Colors.muted },
  row: { flexDirection: 'row', gap: Spacing.md },
  rowItem: { flex: 1 },
  compact: {},
  notes: { minHeight: 88, textAlignVertical: 'top' },
  hint: { fontSize: 12, color: Colors.muted, marginTop: Spacing.xs },
  sub: { fontSize: 13, color: Colors.muted, lineHeight: 19 },
  error: { fontSize: 13, fontWeight: '700', color: Colors.danger },
});
