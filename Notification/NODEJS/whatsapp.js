const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const express = require('express');

const app = express();
app.use(express.json());

// WhatsApp client setup
const client = new Client({
    authStrategy: new LocalAuth(), // Session auto-save karega
    puppeteer: {
        headless: true,
        args: ["--no-sandbox", "--disable-setuid-sandbox"]
    }
});

client.on('qr', qr => {
    console.log('Scan this QR code with WhatsApp:');
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    console.log('WhatsApp client is ready!');
});

// REST API endpoint
app.post('/send-message', async (req, res) => {
    try {
        let { number, message } = req.body;

        // Convert number to WhatsApp format
        number = number.toString().replace(/[^0-9]/g, "");
        if (!number.endsWith("@c.us")) {
            number = `${number}@c.us`;
        }

        console.log(`Sending message to ${number}: ${message}`);
        await client.sendMessage(number, message);

        res.json({ success: true, number, message });
    } catch (err) {
        console.error("Error sending message:", err);
        res.status(500).json({ success: false, error: err.message });
    }
});

client.initialize();

// Start express server
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`API server running on http://localhost:${PORT}`);
});
