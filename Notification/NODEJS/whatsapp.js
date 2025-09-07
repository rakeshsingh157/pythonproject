const { create } = require('@open-wa/wa-automate');
const express = require('express');
const app = express();
app.use(express.json());

let client = null;

// Initialize WhatsApp client
async function initializeWhatsApp() {
    try {
        console.log('Initializing WhatsApp client...');
        
        // Clean up any existing session issues
        const fs = require('fs');
        const path = require('path');
        const sessionPath = path.join(__dirname, 'session');
        
        // Remove any problematic session files
        try {
            if (fs.existsSync(sessionPath)) {
                const stats = fs.statSync(sessionPath);
                if (stats.isDirectory()) {
                    console.log('Cleaning up existing session directory...');
                    fs.rmSync(sessionPath, { recursive: true, force: true });
                }
            }
        } catch (cleanupError) {
            console.log('Session cleanup completed');
        }
        
        client = await create({
            sessionId: 'session',
            multiDevice: true,
            authTimeout: 60,
            blockCrashLogs: true,
            disableSpins: true,
            headless: true,
            hostNotificationLang: 'PT_BR',
            logConsole: true,
            popup: false,
            qrTimeout: 0,
            restartOnCrash: true,
            sessionDataPath: './session',
            useChrome: false,
            chromiumArgs: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--headless',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',
                '--disable-javascript',
                '--disable-default-apps',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding'
            ]
        });
        
        console.log('WhatsApp client initialized successfully!');
        return true;
    } catch (error) {
        console.error('Failed to initialize WhatsApp client:', error);
        return false;
    }
}

// Initialize WhatsApp on startup
initializeWhatsApp();

app.post('/sendMessage', async (req, res) => {
    try {
        const { to, message } = req.body;
        if (!client) {
            return res.status(500).send({ error: "WhatsApp client not ready. Please wait for initialization." });
        }
        
        console.log(`Sending message to ${to}: ${message}`);
        await client.sendText(to, message);
        res.send({ status: "Message sent successfully!" });
    } catch (error) {
        console.error('Error sending message:', error);
        res.status(500).send({ error: "Failed to send message", details: error.message });
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.send({ 
        status: client ? "ready" : "initializing",
        timestamp: new Date().toISOString()
    });
});

app.listen(5000, () => console.log("WhatsApp API running on port 5000"));
