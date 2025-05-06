export type PageItem = {
  sentence: string;
  translation: string;
  explanation: string;
  audio: Blob;
};

export type LanguageSetting = {
  language: string;
  level: string;
  region: string;
  gender: string;
  speaker_name: string;
  request: string;
};

export type VocabularyUpdatePayload = {
  language: string;
  learning_language_idx: number;
  known_words: string[];
  unknown_words: string[];
};
