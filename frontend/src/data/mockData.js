export const mockUser = { id: "u1", name: "Nivar" };

// --- TEXTBOOKS ----------------------------------------------------------
export const mockBooks = [
  {
    id: "b1",
    title: "Introduction to Algorithms",
    author: "Cormen, Leiserson, Rivest, and Stein",
    description:
      "A comprehensive guide to modern algorithm design — from data structures to graph theory and optimization.",
    cover: "/covers/algorithms.jpg",
    chapterCount: 3,
    progress: 45,
  },
  {
    id: "b2",
    title: "Computer Networks",
    author: "Andrew S. Tanenbaum",
    description:
      "An in-depth exploration of how data moves through networks, covering layers, protocols, and network design principles.",
    cover: "/covers/networks.jpg",
    chapterCount: 3,
    progress: 30,
  },
  {
    id: "b3",
    title: "Artificial Intelligence: A Modern Approach",
    author: "Stuart Russell & Peter Norvig",
    description:
      "An introduction to the foundations of AI — including agents, search algorithms, machine learning, and reasoning under uncertainty.",
    cover: "/covers/ai.jpg",
    chapterCount: 2,
    progress: 10,
  },
];

// --- CHAPTERS ----------------------------------------------------------
export const mockChapters = [
  // Algorithms
  { id: "c1", bookId: "b1", title: "Divide and Conquer" },
  { id: "c2", bookId: "b1", title: "Dynamic Programming" },
  { id: "c3", bookId: "b1", title: "Greedy Algorithms" },

  // Networks
  { id: "c4", bookId: "b2", title: "Network Layers" },
  { id: "c5", bookId: "b2", title: "Data Link and Physical Layers" },
  { id: "c6", bookId: "b2", title: "Transport Layer and TCP" },

  // AI
  { id: "c7", bookId: "b3", title: "Intelligent Agents" },
  { id: "c8", bookId: "b3", title: "Search Strategies" },
];

// --- SUMMARIES ----------------------------------------------------------
export const mockSummaries = [
  {
    bookId: "b1",
    chapterId: "c1",
    text:
      "Divide and conquer algorithms split a problem into smaller subproblems, solve them recursively, and combine their solutions. Examples include merge sort, quicksort, and binary search.",
  },
  {
    bookId: "b2",
    chapterId: "c4",
    text:
      "The network layer is responsible for routing packets between devices across potentially multiple networks. It determines optimal paths using protocols like IP, ICMP, and routing algorithms.",
  },
  {
    bookId: "b3",
    chapterId: "c7",
    text:
      "Intelligent agents perceive their environment and act upon it to achieve goals. Key properties include autonomy, reactivity, proactiveness, and social ability.",
  },
];

// --- FLASHCARDS ----------------------------------------------------------
export const mockFlashcards = [
  // Algorithms
  {
    id: "f1",
    bookId: "b1",
    chapterId: "c1",
    front: "What is the core idea behind divide and conquer algorithms?",
    back: "They break a problem into smaller subproblems, solve each recursively, and combine the results.",
  },
  {
    id: "f2",
    bookId: "b1",
    chapterId: "c1",
    front: "Name one classic divide and conquer algorithm.",
    back: "Merge Sort or Quick Sort.",
  },

  // Networks
  {
    id: "f3",
    bookId: "b2",
    chapterId: "c4",
    front: "What is the primary function of the network layer?",
    back: "Routing packets between devices on different networks.",
  },
  {
    id: "f4",
    bookId: "b2",
    chapterId: "c4",
    front: "Which protocol operates at the network layer?",
    back: "Internet Protocol (IP).",
  },

  // AI
  {
    id: "f5",
    bookId: "b3",
    chapterId: "c7",
    front: "What defines an intelligent agent?",
    back: "Its ability to perceive and act rationally within an environment to achieve goals.",
  },
  {
    id: "f6",
    bookId: "b3",
    chapterId: "c7",
    front: "List one property of intelligent agents.",
    back: "Autonomy — acting without external intervention.",
  },
];
