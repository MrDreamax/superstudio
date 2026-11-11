// Détoure le sujet principal d'une photo (détection de sujet Apple, locale, gratuite).
// swift detoure.swift entree.jpg sortie.png  -> PNG transparent, garde SEULEMENT le plus grand sujet (pas le public).
import Vision
import CoreImage
import AppKit
let a = CommandLine.arguments
let ci = CIImage(contentsOf: URL(fileURLWithPath: a[1]))!
let req = VNGenerateForegroundInstanceMaskRequest()
let h = VNImageRequestHandler(ciImage: ci)
try h.perform([req])
let r = req.results!.first!
var best = r.allInstances.first!, bestN = -1
for i in r.allInstances {
    let m = try r.generateScaledMaskForImage(forInstances: IndexSet(integer: i), from: h)
    CVPixelBufferLockBaseAddress(m, .readOnly)
    let w = CVPixelBufferGetWidth(m), hh = CVPixelBufferGetHeight(m), row = CVPixelBufferGetBytesPerRow(m)
    let p = CVPixelBufferGetBaseAddress(m)!.assumingMemoryBound(to: Float32.self)
    var n = 0
    for y in stride(from: 0, to: hh, by: 4) { for x in stride(from: 0, to: w, by: 4) { if p[y * row / 4 + x] > 0.5 { n += 1 } } }
    CVPixelBufferUnlockBaseAddress(m, .readOnly)
    if n > bestN { bestN = n; best = i }
}
let buf = try r.generateMaskedImage(ofInstances: IndexSet(integer: best), from: h, croppedToInstancesExtent: false)
try CIContext().writePNGRepresentation(of: CIImage(cvPixelBuffer: buf), to: URL(fileURLWithPath: a[2]), format: .RGBA8, colorSpace: CGColorSpace(name: CGColorSpace.sRGB)!)
