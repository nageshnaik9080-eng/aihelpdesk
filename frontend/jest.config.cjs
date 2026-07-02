/**
 * Jest is configured with babel-jest (inline presets, no shared babel config file
 * so Vite's own transform is untouched). jsdom environment + Testing Library.
 */
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  testMatch: ['<rootDir>/src/**/*.test.{js,jsx}'],
  moduleNameMapper: {
    '\\.(css|scss|sass|less)$': '<rootDir>/src/__mocks__/styleMock.js',
  },
  transform: {
    '^.+\\.jsx?$': [
      'babel-jest',
      {
        babelrc: false,
        configFile: false,
        presets: [
          ['@babel/preset-env', { targets: { node: 'current' } }],
          ['@babel/preset-react', { runtime: 'automatic' }],
        ],
        plugins: ['babel-plugin-transform-import-meta'],
      },
    ],
  },
};
