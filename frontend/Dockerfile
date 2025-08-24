# Build stage
FROM node:20-alpine AS build-stage

# Set working directory
WORKDIR /app

# Copy package.json and package-lock.json
COPY package*.json ./

# Install ALL dependencies (including dev dependencies for build)
RUN npm install

# Copy the rest of the application code
COPY . .

# Build the frontend for production
RUN npm run build

# Production stage
FROM nginx:alpine AS production-stage

# Copy build output to nginx html directory
# Note: Most modern frontends (Vite, Create React App) output to 'dist' or 'build'
# Adjust the source path based on your frontend framework:
COPY --from=build-stage /app/dist /usr/share/nginx/html
# If using Create React App, use: /app/build instead of /app/dist

# Copy nginx configuration (optional - for custom routing)
# COPY nginx.conf /etc/nginx/nginx.conf

# Expose port 80
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]