# Node.js 18 base image
FROM node:18

WORKDIR /app

# Browser dependencies install karo
RUN apt-get update && apt-get install -y \
    chromium \
    wget \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Package files copy karo
COPY package*.json ./

# Dependencies install karo
RUN npm install

# Baaki code copy karo
COPY . .

# App ka port (agar needed ho)
EXPOSE 3000

# Start command
CMD ["node", "whatsapp.js"]
