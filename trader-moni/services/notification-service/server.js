const dotenv = require('dotenv')
const express = require('express');
const app = express();

dotenv.config()


const config = {
    port: process.env.PORT || 3002,
    serviceName: process.env.SERVICE_NAME || 'notification-service',
    serviceVersion: process.env.SERVICE_VERSION || '1.0.0',
    emailProvider: process.env.EMAIL_PROVIDER || 'mock',
    smsProvider: process.env.SMS_PROVIDER || 'mock'
};

app.use(express.json());

const notifications = [];

app.get('/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        service: config.serviceName,
        version: config.serviceVersion,
        environment: process.env.NODE_ENV || 'development'
    });
});

app.post('/notifications/email', (req, res) => {
    const notification = {
        id: `email-${Date.now()}`,
        type: 'email',
        to: req.body.to,
        subject: req.body.subject,
        message: req.body.message,
        status: 'sent',
        createdAt: new Date().toISOString()
    };
    
    notifications.push(notification);
    console.log(`Email sent to ${notification.to}: ${notification.subject}`);
    
    res.json(notification);
});

app.post('/notifications/sms', (req, res) => {
    const notification = {
        id: `sms-${Date.now()}`,
        type: 'sms',
        to: req.body.to,
        message: req.body.message,
        status: 'sent',
        createdAt: new Date().toISOString()
    };
    
    notifications.push(notification);
    console.log(`SMS sent to ${notification.to}: ${notification.message}`);
    
    res.json(notification);
});

app.get('/notifications/history', (req, res) => {
    res.json(notifications);
});

app.listen(config.port, () => {
    console.log(`${config.serviceName} v${config.serviceVersion} running on port ${config.port}`);
});