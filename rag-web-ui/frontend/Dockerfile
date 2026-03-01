FROM node:22-slim AS base
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .

# Development
FROM base AS dev
EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host"]

# Production build
FROM base AS build
RUN npm run build

FROM nginx:alpine AS production
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
