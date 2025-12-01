// ranksbot.js
const mineflayer = require("mineflayer");

const [,, host, port, nick, rank] = process.argv;

const bot = mineflayer.createBot({
  host: host,
  port: Number(port),
  username: "ranksbot"
});

// Bu funksiya bot tayyor bo‘lgandan keyin buyruq yuboradi
async function giveRank() {
  try {
    // OP yoki permission bo‘lmasa, server buyruqni rad qilishi mumkin
    console.log(`Giving rank '${rank}' to '${nick}'...`);
    
    // 1s kutish, server tayyor bo‘lsin
    await new Promise(res => setTimeout(res, 1000));

    const cmd = `/lp user ${nick} parent set ${rank}`;
    bot.chat(cmd);
    console.log("Sent command:", cmd);

    // AFK-kick oldini olish uchun kichik harakat
    bot.setControlState('forward', true);
    setTimeout(() => bot.setControlState('forward', false), 1200);

    // 2.5s kutib botni chiqazish
    setTimeout(() => {
      bot.quit();
      process.exit(0);
    }, 2500);
  } catch (err) {
    console.error("Error giving rank:", err);
    bot.quit();
    process.exit(1);
  }
}

bot.once("spawn", () => {
  console.log("Bot spawned, waiting to give rank...");
  giveRank();
});

bot.on("kicked", (reason) => {
  console.log("Kicked:", reason);
  process.exit(0);
});

bot.on("error", (err) => {
  console.log("Error:", err);
  process.exit(1);
});
