const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');
const readline = require('readline');

console.log("Initializing WhatsApp Web client...");

// Initialize WhatsApp Client using local auth to preserve session
const client = new Client({
    authStrategy: new LocalAuth(),
    puppeteer: {
        headless: true,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    }
});

client.on('qr', (qr) => {
    console.log('\n--- SCAN THIS QR CODE IN WHATSAPP ---');
    // Generate and render QR code in terminal
    qrcode.generate(qr, { small: true });
});

client.on('ready', () => {
    // Send a clear READY signal back to Python
    console.log('READY_SIGNAL_WHATSAPP');
});

client.on('auth_failure', msg => {
    console.error('Authentication failure:', msg);
});

client.initialize();

// Setup reading from Standard Input for commands from Python
const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
    terminal: false
});

rl.on('line', async (line) => {
    try {
        const cmd = JSON.parse(line.trim());
        if (cmd.action === 'send') {
            const numId = `${cmd.target}@c.us`;
            await client.sendMessage(numId, cmd.message);
            console.log(`MESSAGE_SENT_SUCCESS:${cmd.target}`);
        } else if (cmd.action === 'send_group') {
            const chats = await client.getChats();
            const group = chats.find(chat => chat.isGroup && chat.name === cmd.target);
            if (group) {
                await client.sendMessage(group.id._serialized, cmd.message);
                console.log(`MESSAGE_SENT_GROUP_SUCCESS:${cmd.target}`);
            } else {
                console.log(`ERROR_GROUP_NOT_FOUND:${cmd.target}`);
            }
        }
    } catch (err) {
        console.error("Error parsing/executing command:", err, line);
    }
});
