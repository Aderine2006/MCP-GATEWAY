import os
import subprocess

def run_command(cmd, cwd="."):
    subprocess.run(cmd, cwd=cwd, shell=True, check=True)

# Generate Dockerfile
dockerfile = """FROM node:20-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build
CMD ["npm", "start"]
"""
with open("d:/MCP GATEWAY/enterprise-mcp-gateway/frontend/Dockerfile", "w") as f:
    f.write(dockerfile)

# Basic Dashboard Setup
page_tsx = """import React from 'react';

export default function Dashboard() {
  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold">Enterprise MCP Gateway</h1>
        <p className="text-gray-400">Intelligent Access Layer for AI Agents</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-gray-800 p-6 rounded-lg shadow">
          <h3 className="text-gray-400 text-sm">Total Tools</h3>
          <p className="text-3xl font-bold">12</p>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg shadow">
          <h3 className="text-gray-400 text-sm">Active Agents</h3>
          <p className="text-3xl font-bold">4</p>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg shadow">
          <h3 className="text-gray-400 text-sm">Requests Today</h3>
          <p className="text-3xl font-bold">1,284</p>
        </div>
        <div className="bg-gray-800 p-6 rounded-lg shadow">
          <h3 className="text-gray-400 text-sm">Success Rate</h3>
          <p className="text-3xl font-bold text-green-400">98.7%</p>
        </div>
      </div>

      <div className="bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Live Request Activity</h2>
        <div className="space-y-4">
          <div className="flex justify-between items-center border-b border-gray-700 pb-2">
            <div>
              <p className="font-semibold text-blue-400">CustomerSupportAgent → Support MCP</p>
              <p className="text-sm text-gray-400">get_tickets</p>
            </div>
            <div className="text-right">
              <span className="bg-green-900 text-green-300 px-2 py-1 rounded text-xs">SUCCESS</span>
              <p className="text-xs text-gray-400 mt-1">183ms</p>
            </div>
          </div>
          <div className="flex justify-between items-center border-b border-gray-700 pb-2">
            <div>
              <p className="font-semibold text-blue-400">BillingAgent → Billing MCP</p>
              <p className="text-sm text-gray-400">billing.modify</p>
            </div>
            <div className="text-right">
              <span className="bg-red-900 text-red-300 px-2 py-1 rounded text-xs">403 FORBIDDEN</span>
              <p className="text-xs text-gray-400 mt-1">20ms</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
"""

with open("d:/MCP GATEWAY/enterprise-mcp-gateway/frontend/src/app/page.tsx", "w") as f:
    f.write(page_tsx)
    
print("Frontend populated.")
