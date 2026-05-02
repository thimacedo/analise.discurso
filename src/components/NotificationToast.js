import React, { useEffect, useState } from 'react';
import { messaging } from '../services/firebaseConfig';
import { onMessage } from 'firebase/messaging';

const NotificationToast = () => {
  const [notification, setNotification] = useState(null);

  useEffect(() => {
    const unsubscribe = onMessage(messaging, (payload) => {
      console.log('Mensagem recebida:', payload);
      setNotification(payload.notification);
      setTimeout(() => setNotification(null), 5000);
    });

    return () => unsubscribe();
  }, []);

  if (!notification) return null;

  return (
    <div style={{
      position: 'fixed', top: '20px', right: '20px', padding: '15px',
      backgroundColor: '#333', color: '#fff', borderRadius: '8px', zIndex: 1000
    }}>
      <h4>{notification.title}</h4>
      <p>{notification.body}</p>
    </div>
  );
};

export default NotificationToast;
