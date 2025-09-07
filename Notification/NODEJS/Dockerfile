# Node.js base image use karo
FROM node:18

# App directory banaye
WORKDIR /app

# Package files copy karo
COPY package*.json ./

# Dependencies install karo
RUN npm install

# Baaki code copy karo
COPY . .

# App jo port use karega
EXPOSE 3000

# Start command
CMD ["node", "app.js"]
