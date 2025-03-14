import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import SpeechRecognition , {useSpeechRecognition} from 'react-speech-recognition';
import logo from './assets/Logo.png';
import Refresh_Button from './assets/Refresh_Button.png';
import Window_close from './assets/Window_close.png';
import moon from './assets/Moon.png';
import sunDim from './assets/SunDim.png';
import sent_icon from './assets/Sent_icon.png';
import close from './assets/close.png';
import mic from './assets/mic.png';
import sound from './assets/sound.png';
import './App.css';

function App() {
  const [temp, setTemp] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [darkTheme, setDarkTheme] = useState(false);
  const [loading, setLoading] = useState(false);
  const chatMessagesRef = useRef(null);
  const { transcript, resetTranscript, browserSupportsSpeechRecognition, listening } = useSpeechRecognition();

  const window_close = () => {
    alert("Due to some browser restrictions, the window cannot be closed. Please close the tab manually.")
  };

  const refresh = () => {
    window.location.reload();
  };

  const toggleTheme = () => {
    setDarkTheme(!darkTheme);
  };

  const submitMessage = async (message) => {
    if (message.trim() === "") {
      alert("Please send a message");
      return;
    }
    setChatHistory((history) => [...history, { sender: 'user', text: message }]);
    setTemp('');
    setLoading(true);
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/chat', { query: message });
      const response_data = await response.data;
      console.log("Backend response:", response_data); // Log the response
      setChatHistory((history) => [...history, { sender: 'bot', text: response_data.answer }]);
      // console.log(response_data.response.content);
    } catch (error) {
      console.error("Error sending message:", error);
      alert("Error sending message");
    } finally {
      setLoading(false);
    }
  };

  const removeMarkdown = (text) => {
    return text
      .replace(/[*_~`]/g, "") // Remove *, _, ~, and ` (bold, italic, strikethrough, code)
      .replace(/#+\s?/g, "") // Remove # headers
      .replace(/!\[.*?\]\(.*?\)/g, "") // Remove images
      .replace(/\[.*?\]\(.*?\)/g, "") // Remove links
      .replace(/-\s?/g, "") // Remove list bullets
      .replace(/\n+/g, " "); // Replace newlines with spaces for better flow
  };
  
  const handleSpeak = (markdownText) => {
    if (!markdownText) return; // Prevent empty input
  
    const text = removeMarkdown(markdownText); // Remove Markdown formatting
    speechSynthesis.cancel(); // Stop any ongoing speech
  
    // **Split text into smaller chunks**
    const chunkSize = 20; // Adjust based on needs
    const words = text.split(" ");
    const chunks = [];
  
    for (let i = 0; i < words.length; i += chunkSize) {
      chunks.push(words.slice(i, i + chunkSize).join(" ")); // Create text chunks
    }
  
    let index = 0;
  
    const speakChunks = () => {
      if (index >= chunks.length) return; // Stop when done
  
      const utterance = new SpeechSynthesisUtterance(chunks[index]);
      utterance.rate = 1.0; // Adjust speed
  
      // **Immediately queue next chunk when current finishes**
      utterance.onend = () => {
        index++;
        if (index < chunks.length) {
          speakChunks(); // Speak next chunk immediately
        }
      };
  
      speechSynthesis.speak(utterance);
    };
  
    speakChunks(); // Start speaking
  };
  

  const handlesubmitMessage = (e) => {
    e.preventDefault();
    SpeechRecognition.stopListening(); // Stop speech recognition
    setTemp(transcript); // Set transcribed text to textarea
    resetTranscript(); // Clear the transcript after sending
    submitMessage(temp || transcript);
  };

  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  }, [chatHistory, loading]);

  useEffect(() => {
    if (listening) {
      setTemp(transcript);
      }
    }, [listening, transcript]);
  return (
    <div className={darkTheme ? "App darkTheme" : "App"}>
      <div className='navbar'>
        <img className='logo' src={logo} alt='logo' />
        <div className='right-corner'>
          <img className='Refresh_Button' src={Refresh_Button} alt='Refresh_Button' onClick={refresh} />
          <img className='Window_close' src={Window_close} alt='Window_close' onClick={window_close} />
        </div>
      </div>
      <div className='border'></div>
      <div className="toggle-button" onClick={toggleTheme}>
        <div className={darkTheme ? "right-end" : "left-end"}>
          <img src={darkTheme ? moon : sunDim} alt="Theme Toggle" className={darkTheme ? "halfmoon" : "sun"} />
        </div>
      </div>
      {chatHistory.length === 0 ? (
        <>
          <div className="textbox">
            <p className="text">Hi 👋, I am NIMBOT, Your<br></br>virtual Assistant. How can I<br></br>help you today?</p>
          </div>
          <div className="suggestion">
            <div className="box1" onClick={() => submitMessage("Admission")}>
              <p className="text-style">Admission</p>
            </div>
            <div className="box2" onClick={() => submitMessage("PG Programmes")}>
              <p className="text-style">PG Programmes</p>
            </div>
            <div className="box1" onClick={() => submitMessage("UG Programmes")}>
              <p className="text-style">UG Programmes</p>
            </div>
            <div className="box2" onClick={() => submitMessage("Fee Structure")}>
              <p className="text-style">Fee Structure</p>
            </div>
          </div>
        </>
      ) : (
        <div className="chat-messages" ref={chatMessagesRef}>
          {chatHistory.map((message, index) => (
           <div key={index}>
           <div className={`message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}>
            <ReactMarkdown>{message.text}</ReactMarkdown>
            </div>
            {message.sender === 'bot' && (
        <div className="sound-container">
          <img src={sound} alt="sound" className="sound" onClick={()=>handleSpeak(message.text)}/>
        </div>
      )}
    </div>
  ))}
  {loading && <div className='loading'></div>}
</div>

      )}
      <div className="promp-container">
        {listening ? (
          <>
          <img src={close} alt="check" className="close" onClick={() => { SpeechRecognition.stopListening(); resetTranscript(); }}/>
          <div className="promp-box">
          <textarea
            onChange={(e) => setTemp(e.target.value)}
            className="promp-text"
            placeholder="Write a message..."
            value={listening ? transcript : temp}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault(); // Prevents newline
                handlesubmitMessage(e);
              }
            }}
          />
          {/* <img src={check} alt="check" className="check" onClick={listening ? SpeechRecognition.stopListening : null}/> */}
          <div className="sent-button">
            <img src={sent_icon} alt="Send" className={loading ? "sent-icon icon-blur" : "sent-icon"} onClick={loading ? null : handlesubmitMessage} />
          </div>
        </div>
        </>
        ):(
          <>
          <div className="promp-box">
          <textarea
            onChange={(e) => setTemp(e.target.value)}
            className="promp-text"
            placeholder="Write a message..."
            value={temp}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault(); // Prevents newline
                handlesubmitMessage(e);
              }
            }}
          />
          <div className="sent-button">
          <img src={mic} alt="mic" className={`mic ${!browserSupportsSpeechRecognition ? 'blurred' : ''}`} onClick={browserSupportsSpeechRecognition ? () => { SpeechRecognition.startListening(); setTemp(''); } : null } />
            <img src={sent_icon} alt="Send" className={loading ? "sent-icon icon-blur" : "sent-icon"} onClick={loading ? null : handlesubmitMessage} />
          </div>
        </div> 
        </>
        )}
      </div>
    </div>
  );
}

export default App;
