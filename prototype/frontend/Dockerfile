# Use official Node image
FROM node:22-alpine

# Set working directory
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install --legacy-peer-deps

# Copy app files
COPY . .

# Build app (optional for dev, but standard)
# RUN npm run build

# Run dev server
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
