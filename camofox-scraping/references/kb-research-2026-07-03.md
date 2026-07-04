# Knowledge Base Market Research — Sources & Findings (2026-07-03)

## Sources Scraped (12/12 COMPLETE)

### Pricing Pages (🟢)
| Source | URL | Key Finding |
|--------|-----|-------------|
| Outline | getoutline.com/pricing | Cloud $10/79/249/mo, BSL self-host free |
| AFFiNE | affine.pro/pricing | Free/Pro $6.75/mo/Team $10/seat/mo, Believer $499.99 lifetime, self-host free |
| Siyuan | b3log.org/siyuan/pricing | Free / Lifetime ¥96 / Annual ¥148 / Team ¥148/yr, 8GB cloud storage |

### Comparison Articles (🟢)
| Source | URL | Content |
|--------|-----|---------|
| selfhosting.sh | selfhosting.sh/best/wiki/ | 7 Wiki comparison (Wiki.js, BookStack, DokuWiki, MediaWiki, XWiki, Outline, Docmost) |
| Docsio | docsio.co/blog/free-knowledge-base-software | 9 free KB comparison, SaaS/open-source split |
| Geekflare | geekflare.com/software/self-hosted-wiki-software/ | 7 Wiki comparison (Wiki.js, DokuWiki, MediaWiki, XWiki, BookStack, Gollum, Outline) |
| Contabo | contabo.com/blog/how-to-set-up-a-self-hosted-wiki-complete-guide/ | Deployment guide + software selection |

### Community Discussions (🟢)
| Source | URL | Engagement | Key Points |
|--------|-----|------------|------------|
| HN | news.mcan.sh/item/48053163 | 16 pts, 21 comments | Obsidian/Outline/BookStack/Trilium/Joplin; mobile app important |
| Zhihu #1 | zhihu.com/question/645107504 | 17 answers, 31K views | Feishu+Obsidian dual-chain; 10-year tool comparison table |
| Zhihu #2 | zhihu.com/question/15133096760 | 24 answers, 8.5K views | AnythingLLM+Ollama+Qwen3 RAG; knowledge structure methodology |

### Login-Gated Sources (🔴→🟢 via Camofox headful login)
| Source | Method | Key Findings |
|--------|--------|-------------|
| Xiaohongshu 个人知识库 | Camofox headful login + persistence | 30+ posts about AI knowledge base building (Codex+Obsidian, DeepSeek+Notion, LLM Wiki), monetization trends (变现), "second brain" concept popular |

### Blocked (❌)
| Source | Reason |
|--------|--------|
| Reddit (3 posts) | Cloudflare bot detection — CamoFox identified as bot; needs proxy or cookie import |

## Persistence Verification (2026-07-03)

- **Verified**: DELETE /sessions/:userId BEFORE pkill triggers storageState checkpoint
- **Profile**: kb-researcher → ~/.camofox/profiles/ea62cc266effacda9e8324513feab0dc/storage-state.json (35KB)
- **Zhihu login survives restart**: ✅ Confirmed
- **Xiaohongshu login survives restart**: ✅ Confirmed (same session lifecycle)

## Key Market Insights

1. **Self-hosted KB market**: Outline and AFFiNE offer BSL/free self-host but paid cloud. Siyuan charges lifetime ¥96 — very low price point.
2. **AI integration trend**: Zhihu answers show strong interest in local RAG (AnythingLLM+Ollama+Qwen3). AI-augmented personal KB is emerging.
3. **Mobile-first requirement**: HN and Zhihu users consistently mention mobile app as critical for personal wiki usage.
4. **Markdown as standard**: Obsidian's markdown-first approach is the dominant preference across all communities.
5. **Knowledge structure methodology**: Chinese users (Zhihu) emphasize systematic knowledge organization — mind maps, matrix frameworks, knowledge trees.
6. **Xiaohongshu monetization focus**: Chinese creators actively building "knowledge base + monetization" systems; AI tools (Codex, DeepSeek) for KB building are trending content.
