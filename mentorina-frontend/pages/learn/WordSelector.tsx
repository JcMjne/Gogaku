import { useState } from 'react';
import styles from './WordSelector.module.css';


const normalize = (word: string) =>
  word.toLowerCase().replace(/[.,\s]/g, '');
  

export default function WordSelector({ sentence }: { sentence: string }) {
  const tokens = sentence.replace(/ /g, '_ ').split(/[ +]/).map(token => token.replace(/_/g, ' '));
  
  const [unknownWords, setUnknownWords] = useState<string[]>([]);

  const toggleWord = (word: string) => {
    const norm = normalize(word);
    setUnknownWords((prev) =>
      prev.includes(norm)
        ? prev.filter((w) => w !== norm)
        : [...prev, norm]
    );
  };

  const submitSelectedWords = async () => {
    try {
      const token = localStorage.getItem("token");
      if (!token) {
        alert('Please log in');
        return;
      }
      const response = await fetch('/your-api-endpoint', {
        method: 'POST',
        headers: {
          "Authorization": `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ unknownWords }),
      });
      if (!response.ok) throw new Error('Failed to submit words');
      alert('Selected words submitted successfully!');
    } catch (error) {
      console.error(error);
    }
  };

  return (
    <div className={styles.container}>
      {tokens.map((token, idx) => {
        const norm = normalize(token);
        const isClickable = !/^[、。！？]$/.test(token);
        return isClickable ? (
          <button
            key={idx}
            onClick={() => toggleWord(token)}
            className={unknownWords.includes(norm) ? styles.selectedWord : styles.word}
          >
            <span style={{ whiteSpace: "pre" }}>
              {token}
            </span>
          </button>
        ) : (
          <span key={idx}>{token}</span>
        );
      })}
      <button onClick={submitSelectedWords}>Submit Selected Words</button>
    </div>
  );
}
