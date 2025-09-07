FROM node:18-alpine

# Install Chromium + dependencies + build tools for npm modules
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    freetype-dev \
    harfbuzz \
    ca-certificates \
    ttf-freefont \
    gcompat \
    libstdc++ \
    udev \
    bash \
    python3 \
    make \
    g++

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
