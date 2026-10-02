import { Ionicons } from '@expo/vector-icons';
import { useEvent } from 'expo';
import { useVideoPlayer, VideoView } from 'expo-video';
import type { VideoPlayer } from 'expo-video';
import { useState } from 'react';
import type { GestureResponderEvent, LayoutChangeEvent } from 'react-native';
import { Linking, Pressable, StyleSheet, Text, View } from 'react-native';

import { Colors, Radius, Spacing } from '../lib/theme';
import { Btn } from './ui';

function formatClock(seconds: number) {
  if (!Number.isFinite(seconds) || seconds <= 0) return '0:00';
  const total = Math.floor(seconds);
  const mins = Math.floor(total / 60);
  const secs = total % 60;
  return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
}

function openExternal(uri: string) {
  Linking.openURL(uri).catch(() => undefined);
}

function seekTo(player: VideoPlayer, seconds: number) {
  player.currentTime = seconds;
}

function MediaCard({
  icon,
  label,
  action,
  children,
}: {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  action?: { title: string; uri: string };
  children?: React.ReactNode;
}) {
  return (
    <View style={styles.card}>
      <View style={styles.head}>
        <View style={styles.icon}>
          <Ionicons name={icon} size={14} color={Colors.navy} />
        </View>
        <Text style={styles.label}>{label}</Text>
        {action ? (
          <Pressable onPress={() => openExternal(action.uri)} hitSlop={10} style={styles.link}>
            <Ionicons name="open-outline" size={13} color={Colors.navy} />
            <Text style={styles.linkText}>{action.title}</Text>
          </Pressable>
        ) : null}
      </View>
      {children}
    </View>
  );
}

function VideoSection({ uri }: { uri: string }) {
  const player = useVideoPlayer({ uri }, (p) => {
    p.loop = false;
  });

  return (
    <MediaCard icon="videocam" label="Watch" action={{ title: 'Open', uri }}>
      <View style={styles.videoWrap}>
        <VideoView
          style={styles.video}
          player={player}
          nativeControls
          contentFit="contain"
          allowsPictureInPicture
          fullscreenOptions={{ enable: true }}
        />
      </View>
    </MediaCard>
  );
}

function AudioPlayer({ uri }: { uri: string }) {
  const player = useVideoPlayer({ uri }, (p) => {
    p.loop = false;
    p.timeUpdateEventInterval = 0.5;
  });
  const [trackWidth, setTrackWidth] = useState(0);
  const { isPlaying } = useEvent(player, 'playingChange', { isPlaying: player.playing });
  const progress = useEvent(player, 'timeUpdate', {
    currentTime: player.currentTime,
    currentLiveTimestamp: null,
    currentOffsetFromLive: null,
    bufferedPosition: 0,
  });

  const currentTime = progress?.currentTime ?? 0;
  const duration = player.duration;
  const total = Number.isFinite(duration) && duration > 0 ? duration : 0;
  const position = total > 0 ? Math.min(Math.max(currentTime, 0), total) : 0;
  const percent = total > 0 ? (position / total) * 100 : 0;

  function toggle() {
    if (player.playing) player.pause();
    else player.play();
  }

  function onTrackLayout(e: LayoutChangeEvent) {
    setTrackWidth(e.nativeEvent.layout.width);
  }

  function seek(e: GestureResponderEvent) {
    if (trackWidth <= 0 || total <= 0) return;
    const ratio = Math.min(Math.max(e.nativeEvent.locationX / trackWidth, 0), 1);
    seekTo(player, ratio * total);
  }

  return (
    <MediaCard icon="musical-notes" label="Listen" action={{ title: 'Open', uri }}>
      <View style={styles.audioRow}>
        <Pressable
          onPress={toggle}
          style={styles.playBtn}
          accessibilityRole="button"
          accessibilityLabel={isPlaying ? 'Pause audio' : 'Play audio'}
        >
          <Ionicons name={isPlaying ? 'pause' : 'play'} size={20} color="#FFF" style={styles.playIcon} />
        </Pressable>
        <View style={styles.audioBody}>
          <Pressable onLayout={onTrackLayout} onPress={seek} style={styles.track}>
            <View style={[styles.trackFill, { width: `${percent}%` }]} />
          </Pressable>
          <View style={styles.times}>
            <Text style={styles.time}>{formatClock(position)}</Text>
            <Text style={styles.time}>{total > 0 ? formatClock(total) : '--:--'}</Text>
          </View>
        </View>
      </View>
    </MediaCard>
  );
}

export function SermonMedia({
  videoUrl,
  audioUrl,
  pdfUrl,
  youtubeUrl,
}: {
  videoUrl?: string | null;
  audioUrl?: string | null;
  pdfUrl?: string | null;
  youtubeUrl?: string | null;
}) {
  const hasMedia = Boolean(videoUrl || audioUrl || pdfUrl || youtubeUrl);
  if (!hasMedia) return null;

  return (
    <>
      {videoUrl ? <VideoSection uri={videoUrl} /> : null}
      {audioUrl ? <AudioPlayer uri={audioUrl} /> : null}
      {youtubeUrl || pdfUrl ? (
        <View style={styles.actions}>
          {youtubeUrl ? <Btn title="Watch on YouTube" onPress={() => openExternal(youtubeUrl)} /> : null}
          {pdfUrl ? <Btn title="Open PDF" variant="outline" onPress={() => openExternal(pdfUrl)} /> : null}
        </View>
      ) : null}
    </>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: Colors.card,
    borderRadius: Radius.lg,
    padding: Spacing.lg,
    gap: Spacing.md,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: Colors.border,
    borderLeftWidth: 4,
    borderLeftColor: Colors.navy,
  },
  head: { flexDirection: 'row', alignItems: 'center', gap: Spacing.sm },
  icon: {
    width: 28,
    height: 28,
    borderRadius: 8,
    backgroundColor: Colors.navySoft,
    alignItems: 'center',
    justifyContent: 'center',
  },
  label: {
    flex: 1,
    fontSize: 12,
    fontWeight: '800',
    color: Colors.navy,
    textTransform: 'uppercase',
    letterSpacing: 0.4,
  },
  link: { flexDirection: 'row', alignItems: 'center', gap: 4 },
  linkText: { fontSize: 13, fontWeight: '700', color: Colors.navy },
  videoWrap: { width: '100%', aspectRatio: 16 / 9, borderRadius: Radius.md, overflow: 'hidden', backgroundColor: '#000' },
  video: { width: '100%', height: '100%' },
  audioRow: { flexDirection: 'row', alignItems: 'center', gap: Spacing.md },
  playBtn: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: Colors.navy,
    alignItems: 'center',
    justifyContent: 'center',
  },
  playIcon: { marginLeft: 2 },
  audioBody: { flex: 1, gap: Spacing.xs },
  track: { height: 6, borderRadius: 999, backgroundColor: Colors.border, justifyContent: 'center' },
  trackFill: { height: 6, borderRadius: 999, backgroundColor: Colors.gold },
  times: { flexDirection: 'row', justifyContent: 'space-between' },
  time: { fontSize: 11, fontWeight: '700', color: Colors.muted },
  actions: { gap: Spacing.sm },
});
