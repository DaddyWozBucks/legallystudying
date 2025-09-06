'use client';

import React, { useState, useRef, useEffect } from 'react';
import { api } from '@/lib/api';

interface TTSPlayerProps {
  text: string;
  documentId?: string;
  className?: string;
  autoPlay?: boolean;
  voiceId?: string;
}

export default function TTSPlayer({ 
  text, 
  documentId, 
  className = "", 
  autoPlay = false,
  voiceId 
}: TTSPlayerProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    // Cleanup audio URL when component unmounts
    return () => {
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl);
      }
    };
  }, [audioUrl]);

  const handlePlay = async () => {
    if (isPlaying && audioRef.current) {
      // Pause if already playing
      audioRef.current.pause();
      setIsPlaying(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      let audioBlob: Blob;
      
      if (documentId) {
        // Use document summary endpoint
        audioBlob = await api.speakDocumentSummary(documentId, voiceId);
      } else {
        // Use general TTS endpoint
        audioBlob = await api.generateSpeech(text, voiceId);
      }

      // Create URL for audio blob
      const url = URL.createObjectURL(audioBlob);
      setAudioUrl(url);

      // Play audio
      if (audioRef.current) {
        audioRef.current.src = url;
        await audioRef.current.play();
        setIsPlaying(true);
      }
    } catch (err) {
      console.error('TTS Error:', err);
      setError('Failed to generate speech. Please check your API key.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAudioEnded = () => {
    setIsPlaying(false);
  };

  const handleAudioPause = () => {
    setIsPlaying(false);
  };

  const handleAudioPlay = () => {
    setIsPlaying(true);
  };

  return (
    <div className={`inline-flex items-center gap-2 ${className}`}>
      <button
        onClick={handlePlay}
        disabled={isLoading}
        className={`
          px-4 py-2 rounded-lg flex items-center gap-2 transition-all
          ${isLoading 
            ? 'bg-gray-300 cursor-not-allowed' 
            : isPlaying
            ? 'bg-red-500 hover:bg-red-600 text-white'
            : 'bg-indigo-500 hover:bg-indigo-600 text-white'
          }
        `}
        title={isPlaying ? 'Pause' : 'Play Summary'}
      >
        {isLoading ? (
          <>
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
              <circle 
                className="opacity-25" 
                cx="12" 
                cy="12" 
                r="10" 
                stroke="currentColor" 
                strokeWidth="4"
                fill="none"
              />
              <path 
                className="opacity-75" 
                fill="currentColor" 
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
              />
            </svg>
            <span>Loading...</span>
          </>
        ) : isPlaying ? (
          <>
            <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
              <rect x="6" y="4" width="4" height="16" />
              <rect x="14" y="4" width="4" height="16" />
            </svg>
            <span>Pause</span>
          </>
        ) : (
          <>
            <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
              <path d="M8 5v14l11-7z" />
            </svg>
            <span>Listen to Summary</span>
          </>
        )}
      </button>

      {error && (
        <span className="text-red-500 text-sm">{error}</span>
      )}

      <audio
        ref={audioRef}
        onEnded={handleAudioEnded}
        onPause={handleAudioPause}
        onPlay={handleAudioPlay}
        className="hidden"
      />
    </div>
  );
}