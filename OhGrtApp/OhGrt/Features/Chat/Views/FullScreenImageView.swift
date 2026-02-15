import SwiftUI
import UIKit

struct FullScreenImageView: View {
    let imageURL: URL
    @Environment(\.dismiss) private var dismiss
    @State private var isSaving = false
    @State private var showAlert = false
    @State private var alertMessage = ""
    @State private var imageSaver = ImageSaver()
    @State private var loadedImage: UIImage?
    @State private var isLoading = true
    @State private var loadError: String?

    var body: some View {
        ZStack(alignment: .top) {
            Color.black.ignoresSafeArea()

            Group {
                if let loadedImage {
                    ZoomableImageView(image: loadedImage)
                        .padding(.horizontal, 12)
                } else if isLoading {
                    ProgressView()
                        .progressViewStyle(CircularProgressViewStyle(tint: .white))
                } else {
                    Text(loadError ?? "Unable to load image")
                        .foregroundColor(.white)
                }
            }

            HStack {
                Button {
                    dismiss()
                } label: {
                    HStack(spacing: 6) {
                        Image(systemName: "chevron.left")
                            .font(.system(size: 16, weight: .semibold))
                        Text("Back")
                            .font(.subheadline)
                            .fontWeight(.semibold)
                    }
                    .foregroundColor(.white.opacity(0.9))
                    .padding(.horizontal, 12)
                    .padding(.vertical, 8)
                    .background(Color.black.opacity(0.35))
                    .cornerRadius(16)
                }

                Spacer()

                Button {
                    saveImage()
                } label: {
                    if isSaving {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    } else {
                        Label("Save", systemImage: "square.and.arrow.down")
                            .font(.subheadline)
                            .foregroundColor(.white)
                    }
                }
                .disabled(isSaving)
            }
            .padding(.horizontal, 16)
            .padding(.top, 12)
        }
        .task {
            await loadImage()
        }
        .alert("Save Image", isPresented: $showAlert) {
            Button("OK", role: .cancel) {}
        } message: {
            Text(alertMessage)
        }
    }

    private func loadImage() async {
        isLoading = true
        loadError = nil
        do {
            let (data, _) = try await URLSession.shared.data(from: imageURL)
            guard let image = UIImage(data: data) else {
                throw ImageSaveError.invalidData
            }
            await MainActor.run {
                loadedImage = image
                isLoading = false
            }
        } catch {
            await MainActor.run {
                loadError = error.localizedDescription
                isLoading = false
            }
        }
    }

    private func saveImage() {
        isSaving = true
        Task {
            do {
                let imageToSave: UIImage
                if let loadedImage {
                    imageToSave = loadedImage
                } else {
                    let (data, _) = try await URLSession.shared.data(from: imageURL)
                    guard let image = UIImage(data: data) else {
                        throw ImageSaveError.invalidData
                    }
                    imageToSave = image
                }
                await MainActor.run {
                    imageSaver.save(image: imageToSave) { result in
                        isSaving = false
                        switch result {
                        case .success:
                            alertMessage = "Saved to Photos."
                        case .failure(let error):
                            alertMessage = error.localizedDescription
                        }
                        showAlert = true
                    }
                }
            } catch {
                await MainActor.run {
                    isSaving = false
                    alertMessage = error.localizedDescription
                    showAlert = true
                }
            }
        }
    }
}

enum ImageSaveError: LocalizedError {
    case invalidData

    var errorDescription: String? {
        switch self {
        case .invalidData:
            return "Unable to decode image."
        }
    }
}

final class ImageSaver: NSObject {
    private var completion: ((Result<Void, Error>) -> Void)?

    func save(image: UIImage, completion: @escaping (Result<Void, Error>) -> Void) {
        self.completion = completion
        UIImageWriteToSavedPhotosAlbum(image, self, #selector(saveCompleted(_:didFinishSavingWithError:contextInfo:)), nil)
    }

    @objc private func saveCompleted(_ image: UIImage, didFinishSavingWithError error: Error?, contextInfo: UnsafeRawPointer) {
        if let error {
            completion?(.failure(error))
        } else {
            completion?(.success(()))
        }
        completion = nil
    }
}

struct ZoomableImageView: UIViewRepresentable {
    let image: UIImage

    func makeUIView(context: Context) -> UIScrollView {
        let scrollView = UIScrollView()
        scrollView.minimumZoomScale = 1.0
        scrollView.maximumZoomScale = 4.0
        scrollView.bouncesZoom = true
        scrollView.delegate = context.coordinator
        scrollView.showsVerticalScrollIndicator = false
        scrollView.showsHorizontalScrollIndicator = false
        scrollView.backgroundColor = .black

        let imageView = UIImageView(image: image)
        imageView.contentMode = .scaleAspectFit
        imageView.translatesAutoresizingMaskIntoConstraints = false
        scrollView.addSubview(imageView)

        NSLayoutConstraint.activate([
            imageView.leadingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.leadingAnchor),
            imageView.trailingAnchor.constraint(equalTo: scrollView.contentLayoutGuide.trailingAnchor),
            imageView.topAnchor.constraint(equalTo: scrollView.contentLayoutGuide.topAnchor),
            imageView.bottomAnchor.constraint(equalTo: scrollView.contentLayoutGuide.bottomAnchor),
            imageView.widthAnchor.constraint(equalTo: scrollView.frameLayoutGuide.widthAnchor),
            imageView.heightAnchor.constraint(equalTo: scrollView.frameLayoutGuide.heightAnchor)
        ])

        context.coordinator.imageView = imageView
        return scrollView
    }

    func updateUIView(_ uiView: UIScrollView, context: Context) {
        context.coordinator.imageView?.image = image
    }

    func makeCoordinator() -> Coordinator {
        Coordinator()
    }

    final class Coordinator: NSObject, UIScrollViewDelegate {
        weak var imageView: UIImageView?

        func viewForZooming(in scrollView: UIScrollView) -> UIView? {
            imageView
        }
    }
}

struct IdentifiableURL: Identifiable {
    let id = UUID()
    let url: URL
}
