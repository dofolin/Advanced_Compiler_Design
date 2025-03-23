#include "llvm/IR/IRBuilder.h"
#include "llvm/Pass.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Transforms/Utils/Local.h"
#include <llvm-14/llvm/Transforms/Utils/Local.h>
#include <set>
#include <vector>

using namespace llvm;
using namespace std;

namespace {

struct DeadCodeAnalysis
    : public PassInfoMixin<DeadCodeAnalysis> {
  PreservedAnalyses run(Module &M, ModuleAnalysisManager &AM) {
    for (auto &F : M) {
      for (auto &B : F) {
        for (auto &I : B) {
          if (llvm::isInstructionTriviallyDead(&I, nullptr)) {
            errs() << "TRIVIALLY_DEAD:               " << I << "\n";
          }
          if (llvm::wouldInstructionBeTriviallyDead(&I, nullptr)) {
            errs() << "WOULD_BE_TRIVIALLY_DEAD:      " << I << "\n";
          }
          if (llvm::wouldInstructionBeTriviallyDeadOnUnusedPaths(&I, nullptr)) {
            errs() << "WOULD_BE_DEAD_ON_UNUSED_PATHS:" << I << "\n";
          }
        }
      }
    }
    return PreservedAnalyses::all();
  };
};

} // namespace

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
  return {.APIVersion = LLVM_PLUGIN_API_VERSION,
          .PluginName = "DCE Pass (Totally not copied)",
          .PluginVersion = "v0.1",
          .RegisterPassBuilderCallbacks = [](PassBuilder &PB) {
            PB.registerPipelineStartEPCallback(
                [](ModulePassManager &MPM, OptimizationLevel Level) {
                  MPM.addPass(DeadCodeAnalysis());
                });
          }};
}
