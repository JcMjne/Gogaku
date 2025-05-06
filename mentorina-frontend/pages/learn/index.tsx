import { useEffect, useState } from 'react';
import { getPage, updateVocabulary } from '@/utils/api';
import { PageItem } from '@/types';
import { useRouter } from "next/navigation";
import styles from './WordSelector.module.css';

const normalize = (word: string) =>
  word.toLowerCase().replace(/[.,\s]/g, '');

const decodeSentence = (sentence: string) => {
  return sentence.replace(/ /g, '_ ').split(/[ +]/).map(token => token.replace(/_/g, ' '));
}

export default function LearnPage() {
  const [page, setPage] = useState<PageItem | null>(null);
  const [nextPage, setNextPage] = useState<PageItem | null>(null);
  const [tokens, setTokens] = useState<string[]>([]);
  const [unknownWords, setUnknownWords] = useState<Set<string>>(new Set());
  const [audio, setAudio] = useState<HTMLAudioElement  | null>(null);
  const [langSettings, setLangSettings] = useState<{ language: string, idx: number } | null>(null);
  const router = useRouter();
  
  const fetchLearningLanguageIdx = async () => {
    try {
      const token = localStorage.getItem("token"); // get token from local storage
      if (!token) {
        router.push("/login");
        return;
      }
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/get_current_language_settings`, {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${token}`,
        },
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Failed to fetch learning language index");
      }
      const settings = await res.json();
      setLangSettings({ language: settings.language, idx: settings.learning_language_idx });
    } catch (err: any) {
      alert(err.message || "Failed to fetch learning language index");
    }
  };

  const toggleWord = (word: string) => {
    const norm = normalize(word);
    setUnknownWords((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(norm)) {
        newSet.delete(norm);
      } else {
        newSet.add(norm);
      }
      return newSet;
    });
  };

  // Load page content
  const loadPage = async () => {
    if (!langSettings) return;

    try {
      const token = localStorage.getItem("token");
      if (!token) {
        router.push("/login");
        return;
      }
      const data = await getPage(token, langSettings.idx);
      setNextPage(data);
    } catch (err) {
      alert('Error loading pages: ' + err);
    }
  };

  useEffect(() => {
    fetchLearningLanguageIdx();
  }, []);

  useEffect(() => {
    if (langSettings && !nextPage) {
      loadPage();
    }
  }, [langSettings, nextPage]);

  useEffect(() => {
    if (nextPage && !page) {
      const tokens_decoded = decodeSentence(nextPage.sentence);
      const audioUrl = URL.createObjectURL(nextPage.audio);
      setAudio(new Audio(audioUrl));
      setTokens(tokens_decoded);
      setPage(nextPage);
      setNextPage(null);
    }
  }, [nextPage, page]);

  const handleFeedback = async () => {
    if (!langSettings) return;
    const knownWords = tokens.filter(token => !unknownWords.has(normalize(token)));
    setPage(null); // Set the current page to the next page
    updateVocabulary({
      language: langSettings.language,
      learning_language_idx: langSettings.idx,
      known_words: knownWords,
      unknown_words: Array.from(unknownWords),
    }).catch((err) => {
      console.error('Failed to update vocabulary:', err);
    });
  }

  const playAudio = () => {
    if (audio) {
      audio.play();
    }
  };

  return (
    <div>
      <h1>Learning Page</h1>
      {page ? (
        <div className="p-6 max-w-xl mx-auto">
          <h1 className="text-2xl font-bold mb-4">Learn </h1>
          
          <div className="bg-white shadow p-4 rounded-xl space-y-2">
          <div className={styles.container}>
            {tokens.map((token, idx) => {
              const isClickable = !/^[、。！？]$/.test(token);
              const norm = normalize(token);

              return isClickable ? (
                <button
                  key={idx}
                  onClick={() => toggleWord(token)}
                  className={
                    unknownWords.has(norm)
                      ? styles.selectedWord
                      : styles.word
                  }
                >
                  <span style={{ whiteSpace: "pre" }}>
                    {token}
                  </span>

                </button>
              ) : (
                <span key={idx}>{token}</span>
              );
            })}
          </div>
            <p className="text-gray-700">Translation: {page.translation}</p>
            <p className="text-gray-700">Explanation: {page.explanation}</p>
            <button
              className="mt-2 bg-blue-500 text-white px-3 py-1 rounded"
              onClick={() => playAudio()}
            >
              🔊 Play
            </button>
            <button
              className="mt-2 bg-blue-500 text-white px-3 py-1 rounded"
              onClick={() => handleFeedback()}
            >
              Next
            </button>
          </div>
        </div>
      
      ) : (
        <p>Loading...</p>
      )}
    </div>
  );

}

