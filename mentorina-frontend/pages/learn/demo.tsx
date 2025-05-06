import { useState } from 'react';
import styles from './WordSelector.module.css';
const sentence_ = "この 大胆 な 革新者 は 、 厳格 な 体制 の 恣意的 な 権威 に 堂々 と 異議 を 唱え た 。";
const sentence ="The bold innovator boldly challenged the arbitrary authority of a strict regime in a.";
const sentence___ ="今天+天气+很+好+。";

const normalize = (word: string) =>
  word.toLowerCase().replace(/[.,\s]/g, '');
  
export default function WordSelector() {
  const sentence_ ='안녕하세요. 저+는 한국어+를 배우+고 있+습니다.';

  const tokens = sentence.replace(/ /g, '_ ').split(/[ +]/).map(token => token.replace(/_/g, ' '));

  const [unknownWords, setUnknownWords] = useState<Set<string>>(new Set());

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

  return (
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
  );
}
