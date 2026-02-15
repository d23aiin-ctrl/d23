import SwiftUI
import WebKit

/// UIViewRepresentable wrapping WKWebView for rendering HTML email bodies
struct HTMLBodyView: UIViewRepresentable {
    let htmlContent: String
    @Binding var dynamicHeight: CGFloat
    @Environment(\.colorScheme) var colorScheme

    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.dataDetectorTypes = [.link, .phoneNumber]

        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.scrollView.isScrollEnabled = false
        webView.isOpaque = false
        webView.backgroundColor = .clear
        webView.scrollView.backgroundColor = .clear
        webView.navigationDelegate = context.coordinator
        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {
        let bgColor = colorScheme == .dark ? "#1c1c1e" : "#ffffff"
        let textColor = colorScheme == .dark ? "#e5e5e7" : "#1c1c1e"
        let linkColor = colorScheme == .dark ? "#64d2ff" : "#007aff"

        let styledHTML = """
        <!DOCTYPE html>
        <html>
        <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
                font-size: 15px;
                line-height: 1.5;
                color: \(textColor);
                background-color: \(bgColor);
                margin: 0;
                padding: 12px;
                word-wrap: break-word;
                overflow-wrap: break-word;
            }
            a { color: \(linkColor); }
            img { max-width: 100%; height: auto; border-radius: 8px; }
            table { max-width: 100%; overflow-x: auto; }
            pre, code {
                background: \(colorScheme == .dark ? "#2c2c2e" : "#f2f2f7");
                border-radius: 6px;
                padding: 4px 8px;
                font-size: 13px;
                overflow-x: auto;
            }
            blockquote {
                border-left: 3px solid \(colorScheme == .dark ? "#48484a" : "#c7c7cc");
                margin-left: 0;
                padding-left: 12px;
                color: \(colorScheme == .dark ? "#98989d" : "#8e8e93");
            }
        </style>
        </head>
        <body>\(htmlContent)</body>
        </html>
        """

        webView.loadHTMLString(styledHTML, baseURL: nil)
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, WKNavigationDelegate {
        let parent: HTMLBodyView

        init(_ parent: HTMLBodyView) {
            self.parent = parent
        }

        func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
            webView.evaluateJavaScript("document.body.scrollHeight") { result, _ in
                if let height = result as? CGFloat {
                    DispatchQueue.main.async {
                        self.parent.dynamicHeight = height
                    }
                }
            }
        }

        func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            if navigationAction.navigationType == .linkActivated, let url = navigationAction.request.url {
                UIApplication.shared.open(url)
                decisionHandler(.cancel)
            } else {
                decisionHandler(.allow)
            }
        }
    }
}
