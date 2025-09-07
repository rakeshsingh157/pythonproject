const { create } = require('@open-wa/wa-automate');
const express = require('express');
const app = express();
app.use(express.json());

let client;

create().then(c => client = c);

app.post('/sendMessage', async (req, res) => {
    const { to, message } = req.body;
    if (!client) return res.status(500).send({ error: "Client not ready" });
    await client.sendText(to, message);
    res.send({ status: "Message sent!" });
});

app.listen(5000, () => console.log("WhatsApp API running on port 5000"));