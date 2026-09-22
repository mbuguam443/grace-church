import * as ImagePicker from 'expo-image-picker';
import { useRouter } from 'expo-router';
import { useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { Btn, Card, Chip, Field, SectionTitle } from '../../components/ui';
import { useAuth } from '../../lib/auth';
import { api } from '../../lib/api';
import { Colors, formatDate, initials, Spacing } from '../../lib/theme';

export default function ProfileScreen() {
  const { token, user, member, logout, updateUser, updateMember } = useAuth();
  const router = useRouter();

  const [edit, setEdit] = useState(false);
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [address, setAddress] = useState('');
  const [occupation, setOccupation] = useState('');
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);

  const [showPassword, setShowPassword] = useState(false);
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [changingPassword, setChangingPassword] = useState(false);
  const [passwordMsg, setPasswordMsg] = useState<string | null>(null);

  function startEdit() {
    setPhone(member?.phone ?? '');
    setEmail(user?.email ?? '');
    setAddress(member?.address ?? '');
    setOccupation(member?.occupation ?? '');
    setEdit(true);
  }

  async function saveProfile() {
    if (!token) return;
    setSaving(true);
    setSaveError(null);
    try {
      const res = await api.updateProfile(token, { phone, email, address, occupation });
      updateUser(res.user);
      updateMember(res.member);
      setEdit(false);
    } catch (e) {
      setSaveError(e instanceof Error ? e.message : 'Save failed.');
    } finally {
      setSaving(false);
    }
  }

  async function pickPhoto() {
    if (!token) return;
    const perm = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!perm.granted) {
      Alert.alert('Permission required', 'Photo library access is needed to change your photo.');
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.7,
    });
    if (result.canceled || !result.assets.length) return;
    const asset = result.assets[0];
    const name = asset.fileName || `photo.${asset.mimeType === 'image/png' ? 'png' : 'jpg'}`;
    try {
      const res = await api.uploadPhoto(token, { uri: asset.uri, name, type: asset.mimeType || 'image/jpeg' });
      updateUser(res.user);
      updateMember(res.member);
    } catch (e) {
      Alert.alert('Upload failed', e instanceof Error ? e.message : 'Could not upload photo.');
    }
  }

  async function changePassword() {
    if (!token) return;
    if (!oldPassword || !newPassword) {
      setPasswordMsg('Fill in both password fields.');
      return;
    }
    setChangingPassword(true);
    setPasswordMsg(null);
    try {
      await api.changePassword(token, oldPassword, newPassword);
      setPasswordMsg('Password updated successfully.');
      setOldPassword('');
      setNewPassword('');
      setShowPassword(false);
    } catch (e) {
      setPasswordMsg(e instanceof Error ? e.message : 'Password change failed.');
    } finally {
      setChangingPassword(false);
    }
  }

  function onLogout() {
    Alert.alert('Sign out', 'Are you sure you want to sign out?', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Sign Out', style: 'destructive', onPress: () => logout().then(() => router.replace('/login')) },
    ]);
  }

  const photoUri = user?.photo_url || member?.photo_url;

  return (
    <SafeAreaView style={styles.safe} edges={['top']}>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.title}>Profile</Text>

        <Card style={styles.identity}>
          <View style={styles.avatarWrap}>
            {photoUri ? null : (
              <View style={styles.avatar}>
                <Text style={styles.avatarText}>{initials(user?.full_name)}</Text>
              </View>
            )}
            <Btn title="Change photo" variant="outline" style={styles.photoBtn} onPress={pickPhoto} />
          </View>
          <View style={styles.identityText}>
            <Text style={styles.name}>{user?.full_name}</Text>
            <Text style={styles.username}>@{user?.username}</Text>
            <View style={styles.chips}>
              <Chip label={user?.role_label || 'Member'} />
              {member ? <Chip label={member.membership_status_label} /> : null}
            </View>
          </View>
        </Card>

        <SectionTitle>Personal details</SectionTitle>
        <Card style={styles.sectionCard}>
          <InfoRow label="Member number" value={member?.member_number || '—'} />
          <Divider />
          <InfoRow label="Membership type" value={member?.membership_type_label || '—'} />
          <Divider />
          <InfoRow label="Date joined" value={member ? formatDate(member.date_joined) : '—'} />
          <Divider />
          <InfoRow label="Date of birth" value={member ? formatDate(member.date_of_birth) : '—'} />
          <Divider />
          <InfoRow label="Marital status" value={member ? (member.marital_status || '—') : '—'} />
          <Divider />
          <InfoRow label="Emergency contact" value={member?.emergency_contact_name || '—'} />
          {member?.emergency_contact_phone ? (
            <>
              <Divider />
              <InfoRow label="" value={member.emergency_contact_phone} />
            </>
          ) : null}
        </Card>

        <SectionTitle>Contact information</SectionTitle>
        {!edit ? (
          <Card style={styles.sectionCard}>
            <InfoRow label="Email" value={user?.email || '—'} />
            <Divider />
            <InfoRow label="Phone" value={member?.phone || '—'} />
            <Divider />
            <InfoRow label="Address" value={member?.address || '—'} />
            <Divider />
            <InfoRow label="Occupation" value={member?.occupation || '—'} />
            <Btn title="Edit details" variant="outline" style={styles.inlineBtn} onPress={startEdit} />
          </Card>
        ) : (
          <Card style={styles.sectionCard}>
            <Field label="Email" value={email} onChangeText={setEmail} keyboardType="email-address" autoCapitalize="none" />
            <Field label="Phone" value={phone} onChangeText={setPhone} keyboardType="phone-pad" />
            <Field label="Address" value={address} onChangeText={setAddress} />
            <Field label="Occupation" value={occupation} onChangeText={setOccupation} />
            {saveError ? <Text style={styles.errorText}>{saveError}</Text> : null}
            <View style={styles.btnRow}>
              <Btn title="Cancel" variant="outline" style={styles.flexBtn} onPress={() => setEdit(false)} disabled={saving} />
              <Btn title="Save" style={styles.flexBtn} onPress={saveProfile} loading={saving} />
            </View>
          </Card>
        )}

        <SectionTitle>Password</SectionTitle>
        <Card style={styles.sectionCard}>
          {!showPassword ? (
            <Btn title="Change password" variant="outline" onPress={() => setShowPassword(true)} />
          ) : (
            <>
              <Field label="Current password" value={oldPassword} onChangeText={setOldPassword} secure />
              <Field label="New password" value={newPassword} onChangeText={setNewPassword} secure />
              {passwordMsg ? (
                <Text style={passwordMsg === 'Password updated successfully.' ? styles.successText : styles.errorText}>
                  {passwordMsg}
                </Text>
              ) : null}
              <View style={styles.btnRow}>
                <Btn title="Cancel" variant="outline" style={styles.flexBtn} onPress={() => setShowPassword(false)} />
                <Btn title="Update" style={styles.flexBtn} onPress={changePassword} loading={changingPassword} />
              </View>
            </>
          )}
        </Card>

        <Btn title="Sign Out" variant="danger" onPress={onLogout} />
      </ScrollView>
    </SafeAreaView>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.infoRow}>
      {label ? <Text style={styles.infoLabel}>{label}</Text> : null}
      <Text style={[styles.infoValue, !label && styles.infoValueWide]}>{value}</Text>
    </View>
  );
}

function Divider() {
  return <View style={styles.divider} />;
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: Colors.bg },
  content: { padding: Spacing.lg, gap: Spacing.lg, paddingBottom: Spacing.xl },
  title: { fontSize: 28, fontWeight: '900', color: Colors.navy },
  identity: { flexDirection: 'row', alignItems: 'center', gap: Spacing.lg },
  avatarWrap: { alignItems: 'center', gap: Spacing.sm },
  avatar: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: Colors.navy,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: { color: '#FFF', fontSize: 26, fontWeight: '800' },
  photoBtn: { height: 34, paddingHorizontal: Spacing.sm },
  identityText: { flex: 1, gap: Spacing.xs },
  name: { fontSize: 18, fontWeight: '800', color: Colors.text },
  username: { fontSize: 13, color: Colors.muted },
  chips: { flexDirection: 'row', flexWrap: 'wrap', gap: Spacing.xs, marginTop: Spacing.xs },
  sectionCard: { gap: Spacing.md },
  infoRow: { flexDirection: 'row', alignItems: 'flex-start', gap: Spacing.md },
  infoLabel: { width: 110, fontSize: 13, color: Colors.muted, fontWeight: '600' },
  infoValue: { flex: 1, fontSize: 14, color: Colors.text },
  infoValueWide: { flex: 1 },
  divider: { height: StyleSheet.hairlineWidth, backgroundColor: Colors.border },
  inlineBtn: { alignSelf: 'flex-start', height: 38 },
  flexBtn: { flex: 1 },
  btnRow: { flexDirection: 'row', gap: Spacing.sm },
  errorText: { color: Colors.danger, fontSize: 13 },
  successText: { color: Colors.success, fontSize: 13 },
});