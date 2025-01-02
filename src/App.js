import React, { useState } from 'react'
import logo from './assets/Logo.png'
import Refresh_Button from './assets/Refresh_Button.png'
import Window_close from './assets/Window_close.png'
import moon from './assets/Moon.png'
import sunDim from './assets/SunDim.png'
import sent_icon from './assets/Sent_icon.png'
import './App.css';

function App() {
  const [Temp, setTemp] = useState('')
  const [chatHistory, setChatHistory] = useState([]);

  const window_close=()=>{
    window.close()
  }
  const refresh=()=>{
    window.location.reload()
  }

  const [darkTheme, setDarkTheme] = useState(false);

  const toggleTheme = () => {
    setDarkTheme(!darkTheme);
  };
  const submitMessage = (e) => {
    e.preventDefault();
    setChatHistory((history) => [
      ...history,
      { sender: 'user', text: Temp },
      { sender: 'bot', text: 'This is a bot reply.' } 
    ]);
  };

  return (
    <div className="App">
      <div className='navbar'>
      <img className='logo' src={logo} alt='logo'></img>
      <div className='right-corner'>
      <img className='Refresh_Button' src={Refresh_Button} alt='Refresh_Button' onClick={refresh}></img>              
      <img className='Window_close' src={Window_close} alt='Window_close' onClick={window_close}></img>
      </div>
      </div>
      <div className='border'></div> 
      <div className="toggle-button" onClick={toggleTheme}>
      <div className="button">
        <img src={darkTheme ? moon : sunDim} alt="sunDim" />
      </div>
    </div>
    <div className="textbox">
        <p className='text'>Hi 👋, I am NIMBOT, Your virtual Assistant. How can i help you Today</p>
      </div>
      <div className="suggestion">
        <div className="box1">
            <p className="text-style">Admission</p>
        </div>
        <div className="box2">
        <p className="text-style">PG Programmes</p>
        </div>
        <div className="box1">
        <p className="text-style">UG Programmes</p>
        </div>
        <div className="box2">
        <p className="text-style">Fee Structure</p>
        </div>
      </div>
      <div className="promp-container">
      <div className="promp-box">
        <textarea onChange={(e)=>{
          setTemp(e.target.value)        }}
          className="promp-text"
          placeholder="Write a message..."
        />
        <img src={sent_icon} alt="Send" onClick={submitMessage} />
      </div>
    </div>
    <div>
      {chatHistory.length === 0 ? (
        <>
          <div className="textbox">
            <p className="text">Hi 👋, I am NIMBOT, Your virtual Assistant. How can I help you today?</p>
          </div>
          <div className="suggestion">
        <div className="box1">
            <p className="text-style">Admission</p>
        </div>
        <div className="box2">
        <p className="text-style">PG Programmes</p>
        </div>
        <div className="box1">
        <p className="text-style">UG Programmes</p>
        </div>
        <div className="box2">
        <p className="text-style">Fee Structure</p>
        </div>
      </div>
        </>
      ) : (
        <div className="chat-messages">
          {chatHistory.map((message, index) => (
            <div
              key={index}
              className={`message ${message.sender === 'user' ? 'user-message' : 'bot-message'}`}
            >
              {message.text}
            </div>
          ))}
        </div>
      )}
    </div>
    </div>
  );
}

export default App;
