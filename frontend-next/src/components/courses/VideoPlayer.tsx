"use client";

import { useRef, useState, useEffect, useCallback } from "react";
import dynamic from "next/dynamic";
import { Gauge, SkipForward } from "lucide-react";
import { useLanguage } from "@/context/LanguageContext";

const ReactPlayer = dynamic(() => import("react-player"), { ssr: false });

interface VideoPlayerProps {
  src?: string;
  duration: number;
  initialWatched: number;
  onProgress: (seconds: number) => void;
  onDurationLoaded?: (seconds: number) => void;
  disabled?: boolean;
  isPremium?: boolean;
}

export function VideoPlayer({ 
  src, 
  duration, 
  initialWatched, 
  onProgress, 
  onDurationLoaded, 
  disabled = false, 
  isPremium = false 
}: VideoPlayerProps) {
  const { t } = useLanguage();
  const playerRef = useRef<any>(null);
  const [mounted, setMounted] = useState(false);
  const [watched, setWatched] = useState(initialWatched);
  const [playbackRate, setPlaybackRate] = useState(1.0);
  const [showSpeedMenu, setShowSpeedMenu] = useState(false);
  const [showSkipWarning, setShowSkipWarning] = useState(false);
  const lastSent = useRef(0);
  const maxReached = useRef(initialWatched);
  const skipFlagRef = useRef(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  const videoSrc = src?.startsWith("http") ? src : src ? (src.startsWith("/") ? src : `/uploads/${src}`) : undefined;
  
  // Cast ReactPlayer to any for React 19 compatibility
  const Player = ReactPlayer as any;

  // Synchronize initial progress when loaded asynchronously
  const [hasSetInitialProgress, setHasSetInitialProgress] = useState(false);

  // Reset state when the video URL changes
  useEffect(() => {
    maxReached.current = initialWatched;
    lastSent.current = initialWatched;
    setWatched(initialWatched);
    setHasSetInitialProgress(false);
  }, [src]);

  useEffect(() => {
    if (initialWatched > 0 && !hasSetInitialProgress && playerRef.current) {
      playerRef.current.seekTo(initialWatched, 'seconds');
      maxReached.current = initialWatched;
      lastSent.current = initialWatched;
      setWatched(initialWatched);
      setHasSetInitialProgress(true);
    }
  }, [initialWatched, hasSetInitialProgress, mounted]);

  const handleProgress = useCallback((state: { playedSeconds: number }) => {
    if (disabled || skipFlagRef.current) return;
    
    const playedSeconds = state.playedSeconds;
    const current = Math.floor(playedSeconds);

    if (current > maxReached.current) {
      maxReached.current = current;
    }
    
    if (current > lastSent.current) {
      lastSent.current = current;
      setWatched(current);
      onProgress(current);
    }
  }, [disabled, onProgress]);

  const handleSeek = useCallback((seconds: number) => {
    if (disabled) return;
    
    // Increased threshold to 15 to prevent false-positives caused by short buffering jumps
    if (seconds > maxReached.current + 15) {
      skipFlagRef.current = true;
      if (playerRef.current) {
        playerRef.current.seekTo(maxReached.current, 'seconds');
      }
      
      setShowSkipWarning(true);
      setTimeout(() => setShowSkipWarning(false), 2500);
      setTimeout(() => { skipFlagRef.current = false; }, 500);
    } else {
      if (seconds > maxReached.current) {
        maxReached.current = Math.floor(seconds);
      }
    }
  }, [disabled]);

  const handleSpeedChange = (rate: number) => {
    setPlaybackRate(rate);
    setShowSpeedMenu(false);
  };

  const speedOptions = [1.0, 1.25, 1.5, 2.0];
  const speedMenuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (speedMenuRef.current && !speedMenuRef.current.contains(event.target as Node)) {
        setShowSpeedMenu(false);
      }
    };
    if (showSpeedMenu) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [showSpeedMenu]);

  if (!mounted) {
    return <div className="relative bg-black rounded-lg overflow-hidden aspect-video skeleton-pulse" />;
  }

  return (
    <div className="relative bg-black rounded-lg overflow-hidden aspect-video">
      {videoSrc ? (
        <>
          {/* No-skip warning overlay */}
          {showSkipWarning && (
            <div className="absolute top-4 left-1/2 -translate-x-1/2 z-30 flex items-center gap-2 bg-black/80 text-white px-4 py-2 rounded-lg text-sm font-medium backdrop-blur-sm border border-white/20 animate-in fade-in slide-in-from-top-2">
              <SkipForward className="w-4 h-4 text-amber-400" />
              <span>{t("videoNoSkipWarning")}</span>
            </div>
          )}

          <div className="w-full h-full">
            <Player
              ref={playerRef}
              url={videoSrc}
              controls={!disabled}
              width="100%"
              height="100%"
              progressInterval={1000}
              playbackRate={isPremium ? playbackRate : 1.0}
              onProgress={handleProgress}
              onSeek={handleSeek}
              onDuration={(dur: number) => {
                if (onDurationLoaded) onDurationLoaded(Math.floor(dur));
              }}
              onReady={() => {
                if (initialWatched > 0 && playerRef.current && !hasSetInitialProgress) {
                  playerRef.current.seekTo(initialWatched, 'seconds');
                  maxReached.current = initialWatched;
                  lastSent.current = initialWatched;
                  setHasSetInitialProgress(true);
                }
              }}
              config={{
                youtube: {
                  playerVars: { 
                    showinfo: 0, 
                    rel: 0, 
                    modestbranding: 1,
                    origin: typeof window !== 'undefined' ? window.location.origin : undefined
                  }
                },
                file: {
                  attributes: {
                    controlsList: 'nodownload'
                  }
                }
              }}
            />
          </div>

          {/* Speed controls for Premium */}
          {isPremium && !disabled && (
            <div className="absolute top-4 right-4 z-10">
              <div className="relative" ref={speedMenuRef}>
                <button
                  type="button"
                  onClick={() => setShowSpeedMenu(!showSpeedMenu)}
                  className="bg-black/70 hover:bg-black/90 text-white px-3 py-2 rounded-lg flex items-center gap-2 text-sm font-medium transition-colors backdrop-blur-sm"
                  title={t("playbackSpeed")}
                >
                  <Gauge className="w-4 h-4" />
                  <span>{playbackRate}x</span>
                </button>
                {showSpeedMenu && (
                  <div className="absolute top-full right-0 mt-2 bg-black/90 backdrop-blur-sm rounded-lg overflow-hidden shadow-xl border border-white/10">
                    {speedOptions.map((rate) => (
                      <button
                        key={rate}
                        type="button"
                        onClick={() => handleSpeedChange(rate)}
                        className={`w-full px-4 py-2 text-left text-sm text-white hover:bg-white/10 transition-colors ${
                          playbackRate === rate ? "bg-purple-600/50 font-semibold" : ""
                        }`}
                      >
                        {rate}x
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="w-full h-full flex items-center justify-center text-gray-400 bg-gray-900">
          <p>{t("noVideoFiles")}</p>
        </div>
      )}
    </div>
  );
}
