"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const proseClasses =
  "prose prose-gray dark:prose-invert max-w-none prose-headings:font-semibold prose-h2:mt-8 prose-h2:mb-3 prose-h2:text-lg prose-h3:mt-6 prose-h3:mb-2 prose-h3:text-base prose-p:my-3 prose-ul:my-3 prose-ol:my-3 prose-li:my-0.5 prose-code:bg-gray-100 dark:prose-code:bg-gray-800 prose-code:px-1.5 prose-code:py-0.5 prose-code:rounded prose-code:text-sm prose-pre:bg-gray-900 prose-pre:border prose-pre:border-gray-700 prose-pre:rounded-lg prose-pre:overflow-x-auto";

export function TopicTheoryContent({ content }: { content: string }) {
  return (
    <div className={`${proseClasses} text-gray-700 dark:text-gray-300`}>
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          code({ node, className, children, ...props }) {
            const isBlock = className != null;
            if (isBlock) {
              return (
                <code className={className} {...props}>
                  {children}
                </code>
              );
            }
            return (
              <code
                className="bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded text-sm font-mono"
                {...props}
              >
                {children}
              </code>
            );
          },
          pre({ children }) {
            return (
              <pre className="bg-gray-900 dark:bg-gray-950 text-gray-100 p-4 rounded-lg border border-gray-700 overflow-x-auto my-4">
                {children}
              </pre>
            );
          },
        }}
      >
        {content}
      </ReactMarkdown>
    </div>
  );
}
