import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

export interface TableLang {
  [language: string]: {
    spacy: string;
    lang_code: string;
    speaker_names: {
      [region: string]: {
        FEMALE?: string[];
        MALE?: string[];
      };
    };
  };
}

const LanguageSettingForm = () => {
  const [languages, setLanguages] = useState<TableLang>({});
  const [selectedLanguage, setSelectedLanguage] = useState("");
  const [level, setLevel] = useState("");
  const [geminiRequest, setGeminiRequest] = useState("");
  const [additionalWords, setAdditionalWords] = useState("");
  const [region, setRegion] = useState("");
  const [gender, setGender] = useState<"FEMALE" | "MALE" | "">("");
  const [speakerName, setSpeakerName] = useState("");
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) {
      router.push("/login");
      return;
    }
    const fetchInitialData = async () => {
      try {
        const [langRes, currentLangRes] = await Promise.all([
          fetch(`${process.env.NEXT_PUBLIC_API_URL}/table_lang`),
          fetch(`${process.env.NEXT_PUBLIC_API_URL}/get_current_language`, {
            headers: { Authorization: `Bearer ${token}` },
          }),
        ]);
  
        if (!langRes.ok || !currentLangRes.ok) {
          throw new Error("Failed to fetch initial data");
        }
  
        const langData = await langRes.json();
        const currentLangData = await currentLangRes.json();
  
        setLanguages(langData);
        if (!selectedLanguage) {
          setSelectedLanguage(currentLangData.current_language);
        }
      } catch (err) {
        console.error("Error fetching initial data", err);
      }
    };
  
    fetchInitialData();

    if (selectedLanguage) {
      fetch(`${process.env.NEXT_PUBLIC_API_URL}/get_language_setting?language=${selectedLanguage}`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      .then(res => {
        if (!res.ok) throw new Error("not found");
        return res.json();
      })
      .then(data => {
        setLevel(data.level);
        setGeminiRequest(data.request);
        setAdditionalWords(data.additional_words);
        setRegion(data.region);
        setGender(data.gender);
        setSpeakerName(data.speaker_name)});
    }
  }, [selectedLanguage]);

  useEffect(() => {
    if (
      selectedLanguage &&
      languages[selectedLanguage]?.speaker_names &&
      Object.keys(languages[selectedLanguage].speaker_names).length > 0 &&
      !region
    ) {
      const firstRegion = Object.keys(languages[selectedLanguage].speaker_names)[0];
      setRegion(firstRegion);
    }
  }, [selectedLanguage, languages, region]);

  useEffect(() => {
    if (
      selectedLanguage &&
      region &&
      languages[selectedLanguage]?.speaker_names?.[region] &&
      Object.keys(languages[selectedLanguage].speaker_names[region]).length > 0 &&
      !gender
    ) {
      const firstGender = Object.keys(languages[selectedLanguage].speaker_names[region])[0] as "MALE" | "FEMALE";
      setGender(firstGender);
    }
  }, [selectedLanguage, region, languages, gender]);

  useEffect(() => {
    if (selectedLanguage && region && gender && !speakerName) {
      const speakerList =
        languages[selectedLanguage]?.speaker_names?.[region]?.[gender];
  
      if (speakerList && speakerList.length > 0) {
        setSpeakerName(speakerList[0]);
      }
    }
  }, [selectedLanguage, region, gender, languages, speakerName]);

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const token = localStorage.getItem("token");

    const payload = {
      language: selectedLanguage,
      level: level,
      region: region,
      gender: gender,
      speaker_name: speakerName,
      request: geminiRequest,
    };
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/set_language_setting`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });
  
      if (!response.ok) {
        const error = await response.json();
        alert("Error occurred while saving settings" + error.detail);
        return;
      }
  
    } catch (error) {
      console.error("Error", error);
      alert("Error occurred while saving settings.");
    }  
  };

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedLanguage(e.target.value);
  };

  const handleRegionChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setRegion(e.target.value);
    setGender(""); // Reset gender when region changes
  };

  const handleGenderChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setGender(e.target.value as "FEMALE" | "MALE");
  };

  const handleSpeakerChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSpeakerName(e.target.value);
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Select Language */}
      <div>
        <label htmlFor="language">Language to learn:</label>
        <select
          id="language"
          value={selectedLanguage}
          onChange={handleLanguageChange}
        >
          {Object.keys(languages).map((language) => (
            <option key={language} value={language}>
              {language}
            </option>
          ))}
        </select>
      </div>
      
      {/* Level */}
      <div>
        <label htmlFor="level">Level:</label>
        <input
          type="text"
          id="level"
          value={level}
          onChange={(e) => setLevel(e.target.value)}
        />
      </div>

      {/* Request */}
      <div>
        <label htmlFor="geminiRequest">Request:</label>
        <textarea
          id="geminiRequest"
          value={geminiRequest}
          onChange={(e) => setGeminiRequest(e.target.value)}
        />
      </div>

      {/* Add words to learn */}
      <div>
        <label htmlFor="additionalWords">Add words to learn:</label>
        <textarea
          id="additionalWords"
          value={additionalWords}
          onChange={(e) => setAdditionalWords(e.target.value)}
        />
      </div>

      {/* Speaker region */}
      <div>
        <label htmlFor="region">Speaker region:</label>
        <select
          id="region"
          value={region}
          onChange={handleRegionChange}
        >
          {selectedLanguage &&
          languages[selectedLanguage] &&
          languages[selectedLanguage].speaker_names &&
          Object.keys(languages[selectedLanguage].speaker_names).map((region) => (
            <option key={region} value={region}>
              {region}
            </option>
          ))}
        </select>
      </div>

      {/* Speaker gender */}
      <div>
        <label htmlFor="gender">Speaker gender:</label>
        <select
          id="gender"
          value={gender}
          onChange={handleGenderChange}
        >
          {region &&
            languages[selectedLanguage]?.speaker_names[region] &&
            Object.keys(languages[selectedLanguage].speaker_names[region]).map(
              (gender) => (
                <option key={gender} value={gender}>
                  {gender}
                </option>
              )
            )}
        </select>
      </div>

      {/* Speaker selection */}
      <div>
        <label htmlFor="speaker">Speaker name:</label>
        <select
          id="speaker"
          value={speakerName}
          onChange={handleSpeakerChange}
        >
          {gender &&
            region &&
            languages[selectedLanguage]?.speaker_names[region]?.[gender]?.map(
              (name) => (
                <option key={name} value={name}>
                  {name}
                </option>
              )
            )}
        </select>
      </div>

      <button type="submit">Save settings</button>
    </form>
  );
};

export default LanguageSettingForm;
