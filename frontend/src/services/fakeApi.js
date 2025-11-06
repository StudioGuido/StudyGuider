import {
  mockUser, mockBooks, mockChapters, mockSummaries, mockFlashcards
} from "../data/mockData";

const delay = (ms = 200) => new Promise(r => setTimeout(r, ms));

export const fakeApi = {
  getUser: async () => { await delay(); return mockUser; },
  getBooks: async () => { await delay(); return mockBooks; },
  getChapters: async (bookId) => { await delay(); return mockChapters.filter(c => c.bookId === bookId); },
  getSummary: async (bookId, chapterId) => {
    await delay();
    return mockSummaries.find(s => s.bookId === bookId && s.chapterId === chapterId) ?? null;
  },
  getFlashcards: async (bookId, chapterId) => {
    await delay();
    return mockFlashcards.filter(f => f.bookId === bookId && f.chapterId === chapterId);
  },
};
