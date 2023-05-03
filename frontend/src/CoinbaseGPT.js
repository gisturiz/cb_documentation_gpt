import React, { useState } from 'react';
import axios from 'axios';
import { Rings } from 'react-loader-spinner';
import './CoinbaseGPT.css';

function CoinbaseGPT() {
    const [inputValue, setInputValue] = useState('');
    const [responseData, setResponseData] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    const handleInputChange = (event) => {
        setInputValue(event.target.value);
    };

    const sendRequestToBackend = async () => {
        setIsLoading(true);
        axios.post("https://coinbase-cloud-docs.herokuapp.com/predict", { "text": inputValue })
            .then(response => {
                setInputValue('');
                setIsLoading(false);
                setResponseData(response.data);
            })
            .catch(error => { console.log(error); });
    };

    return (
        <div className="coinbase-chatgpt">
            <h1 className="coinbase-chatgpt-title">Coinbase Documentation GPT</h1>
            <a className="coinbase-chatgpt-documentation" href="https://docs.cloud.coinbase.com/" target="_blank" rel="noreferrer">Coinbase Official Documentation</a>
            <div className="coinbase-chatgpt-input-container">
                <input
                    type="text"
                    className="coinbase-chatgpt-input"
                    value={inputValue}
                    onChange={handleInputChange}
                    placeholder="Type your question here..."
                />
                <button className="coinbase-chatgpt-button" onClick={sendRequestToBackend} disabled={!inputValue}>
                    Send
                </button>
            </div>
            {isLoading ? <div className="coinbase-chatgpt-response"><Rings color="#1452f0" /></div> :
                responseData ? (<>
                    <div className="coinbase-chatgpt-response">
                        <strong>{responseData.question}</strong><br />
                        {responseData.answer}
                    </div>
                    <div className="coinbase-chatgpt-response-source">
                        Source:<a href={responseData.url} target="_blank" rel="noreferrer">{responseData.url}</a>
                    </div></>) : null}
        </div>
    );
}

export default CoinbaseGPT;