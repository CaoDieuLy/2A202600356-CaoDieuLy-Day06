"use client";

import { useState, useRef, useEffect } from 'react';
import Image from 'next/image';

// Thêm Logo vào thư mục src/app/ (Sử dụng đường dẫn tuyệt đối hoặc relative)
import vnaLogo from './logo-vna-mobile.png';

type Message = {
  id: string;
  role: 'user' | 'bot';
  content: string;
};

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: 'welcome',
      role: 'bot',
      content: 'Xin chào, tôi là NEOv2.0 - Trợ lý ảo của Vietnam Airlines. Rất vui được hỗ trợ bạn!\n\nDưới đây là một số việc tôi có thể giúp:\nTra cứu chuyến bay: Kiểm tra tình trạng, giờ cất/hạ cánh\nQuản lý vé: Xem lại thông tin đặt chỗ cá nhân.\nTra cứu giá vé: Tham khảo giá tốt nhất giữa các chặng.\nQuy định hành lý: Tư vấn chi tiết số kiện, số cân xách tay/ký gửi cho từng hạng vé.\n\nBạn cần tôi hỗ trợ vấn đề gì?'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e?: React.FormEvent, textOverride?: string) => {
    if (e) e.preventDefault();
    const userMsg = textOverride || input.trim();
    if (!userMsg || isLoading) return;

    if (!textOverride) setInput('');
    
    // Thêm tin nhắn user vào UI
    const newUserMsg: Message = { id: Date.now().toString(), role: 'user', content: userMsg };
    setMessages(prev => [...prev, newUserMsg]);
    setIsLoading(true);

    try {
      const res = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg })
      });

      if (!res.ok) throw new Error('Network response was not ok');
      const data = await res.json();
      
      let botText = '';
      if (data.error) {
        botText = `Lỗi Backend: ${data.error}`;
      } else {
        botText = data.response;
      }
      
      const newBotMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: 'bot',
        content: botText || 'Xin lỗi, hệ thống đang gặp gián đoạn nhỏ.'
      };
      
      setMessages(prev => [...prev, newBotMsg]);
    } catch (error) {
      console.error('Error fetching chat:', error);
      setMessages(prev => [
        ...prev, 
        { id: Date.now().toString(), role: 'bot', content: 'Có lỗi xảy ra khi kết nối máy chủ. Vui lòng kiểm tra xem Backend (FastAPI) đã được bật chưa.' }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleQuickReply = (text: string) => {
    handleSubmit(undefined, text);
  };

  const renderMessageContent = (content: string) => {
    const formatted = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br/>');
        
    return <div dangerouslySetInnerHTML={{ __html: formatted }} />;
  };

  return (
    <div className="chat-container">
      {/* Header Teal của VNA */}
      <div className="chat-header">
        <div className="header-left">
          <div className="avatar">
            <Image src={vnaLogo} alt="Vietnam Airlines Logo" width={100} height={30} style={{ objectFit: "contain" }} />
          </div>
        </div>
        <div className="header-actions">
          <span>⚙️</span>
          <span>✕</span>
        </div>
      </div>

      <div className="messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`message ${msg.role}`}>
            {renderMessageContent(msg.content)}
          </div>
        ))}
        
        {isLoading && (
          <div className="message bot">
            <div className="typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Gợi ý nếu chỉ mới có tin nhắn Welcome */}
      {messages.length === 1 && (
        <div className="quick-replies">
          <button className="quick-reply-btn" onClick={() => handleQuickReply('Hành lý xách tay hạng phổ thông')}>
            Hành lý xách tay
          </button>
          <button className="quick-reply-btn" onClick={() => handleQuickReply('Tra cứu trạng thái VN123 hnay')}>
            Chuyến bay hôm nay
          </button>
          <button className="quick-reply-btn" onClick={() => handleQuickReply('Giá vé Hà Nội - Sài Gòn')}>
            Giá vé chặng đi
          </button>
          <button className="quick-reply-btn" onClick={() => handleQuickReply('Kiểm tra vé NGUYEN/DUNG BP')}>
            Quản lý vé
          </button>
        </div>
      )}

      <div className="message-form-container">
        <form onSubmit={e => handleSubmit(e)} className="message-form">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Nhập câu hỏi của Quý khách tại đây..."
            className="message-input"
            disabled={isLoading}
          />
          <button type="submit" disabled={!input.trim() || isLoading} className="send-button">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </form>
        <div className="disclaimer">
          NEO có thể sai sót, hãy kiểm tra thông tin quan trọng.<br/>
          <a href="#">Điều khoản sử dụng</a>
        </div>
      </div>
    </div>
  );
}
