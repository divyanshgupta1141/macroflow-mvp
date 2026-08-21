import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "MacroFlow AI — Cross-Fleet Engine",
  description: "Autonomous agent optimizing high-protein meal combinations across restaurant food delivery and quick-commerce grocery fleets.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" suppressHydrationWarning className="dark">
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                if (typeof window === 'undefined') return;

                // 1. Trap all errors originating from third-party Chrome extensions (e.g. chrome-extension://)
                // to prevent Next.js Dev Overlay from displaying third-party extension crashes.
                window.addEventListener('error', function(event) {
                  var isExtError = (
                    (event.filename && event.filename.indexOf('chrome-extension://') !== -1) ||
                    (event.message && (event.message.indexOf("reading 'M_ID'") !== -1 || event.message.indexOf("M_ID") !== -1))
                  );
                  if (isExtError) {
                    event.stopImmediatePropagation();
                    event.preventDefault();
                    return true;
                  }
                }, true);

                window.addEventListener('unhandledrejection', function(event) {
                  var stack = (event.reason && (event.reason.stack || event.reason.message)) || '';
                  if (stack.indexOf('chrome-extension://') !== -1 || stack.indexOf('M_ID') !== -1) {
                    event.stopImmediatePropagation();
                    event.preventDefault();
                  }
                }, true);

                // 2. Define fallback property getters across global prototypes for M_ID
                try {
                  var safeProp = {
                    get: function() { return '1'; },
                    set: function(val) {},
                    configurable: true,
                    enumerable: false
                  };

                  if (!('M_ID' in Object.prototype)) {
                    Object.defineProperty(Object.prototype, 'M_ID', safeProp);
                  }
                  if (typeof Element !== 'undefined' && !('M_ID' in Element.prototype)) {
                    Object.defineProperty(Element.prototype, 'M_ID', safeProp);
                  }
                  window.M_ID = '1';
                  if (typeof document !== 'undefined') {
                    document.M_ID = '1';
                  }
                } catch(e) {}

                // 3. Strip browser-extension injected attributes (bis_skin_checked, etc.)
                try {
                  var cleanNode = function(node) {
                    if (node && node.nodeType === 1) {
                      if (node.hasAttribute('bis_skin_checked')) node.removeAttribute('bis_skin_checked');
                      if (node.hasAttribute('bis_size')) node.removeAttribute('bis_size');
                      if (node.hasAttribute('bis_id')) node.removeAttribute('bis_id');
                    }
                  };

                  var observer = new MutationObserver(function(mutations) {
                    for (var i = 0; i < mutations.length; i++) {
                      var m = mutations[i];
                      if (m.type === 'attributes' && m.attributeName && m.attributeName.indexOf('bis_') === 0) {
                        m.target.removeAttribute(m.attributeName);
                      } else if (m.type === 'childList') {
                        for (var j = 0; j < m.addedNodes.length; j++) {
                          var node = m.addedNodes[j];
                          cleanNode(node);
                          if (node && node.querySelectorAll) {
                            var els = node.querySelectorAll('[bis_skin_checked], [bis_size], [bis_id]');
                            for (var k = 0; k < els.length; k++) {
                              cleanNode(els[k]);
                            }
                          }
                        }
                      }
                    }
                  });

                  observer.observe(document.documentElement, {
                    attributes: true,
                    childList: true,
                    subtree: true,
                    attributeFilter: ['bis_skin_checked', 'bis_size', 'bis_id']
                  });
                } catch(e) {}
              })();
            `,
          }}
        />
      </head>
      <body
        className={`bg-[#090D14] text-zinc-100 antialiased min-h-screen ${geistSans.variable} ${geistMono.variable}`}
        suppressHydrationWarning
      >
        {children}
      </body>
    </html>
  );
}
