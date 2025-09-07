FROM node:18-alpine

# Install Chromium + dependencies + build tools for npm modules
RUN apk add --no-cache \
    libatk1.0-0t64 \
  libc6 \
  libcairo2 \
  libcups2t64 \
  libdbus-1-3 \
  libexpat1 \
  libfontconfig1 \
  libgcc-s1 \
  libgdk-pixbuf2.0-0 \
  libglib2.0-0t64 \
  libgtk-3-0t64 \
  libnspr4 \
  libpango-1.0-0 \
  libx11-6 \
  libx11-xcb1 \
  libxcb1 \
  libxcomposite1 \
  libxcursor1 \
  libxdamage1 \
  libxext6 \
  libxfixes3 \
  libxi6 \
  libxrandr2 \
  libxrender1 \
  libasound2t64 \
  libatk-bridge2.0-0t64 \
  ca-certificates \
  fonts-liberation \
  libnss3 \
  lsb-release \
  xdg-utils \
  wget

# Puppeteer environment
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true \
    PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

# Working directory
WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S whatsapp -u 1001

# Copy package files for caching
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy application code
COPY . .

# Create session folder
RUN mkdir -p /app/session && chown -R whatsapp:nodejs /app

# Switch to non-root user
USER whatsapp

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:5000/health', (res) => { process.exit(res.statusCode === 200 ? 0 : 1) })"

# Start app
CMD ["node", "whatsapp.js"]
