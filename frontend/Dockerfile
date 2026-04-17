# 1. Use Node 20 or 22 to satisfy Vite's requirements
FROM node:22 AS build

WORKDIR /app

# 2. Copy only package files first (better caching)
COPY package*.json ./

# 3. Clean install (avoids architecture mismatches from your Mac)
RUN npm ci

COPY . .

# 4. Use BUILD, not dev
RUN npm run build

# Stage 2: Serve
FROM node:22-alpine

WORKDIR /app
RUN npm install -g serve
COPY --from=build /app/dist ./dist

EXPOSE 3000
CMD ["serve", "-s", "dist"]