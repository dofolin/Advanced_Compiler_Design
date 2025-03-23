#include "llvm/Pass.h"
#include "llvm/Passes/PassBuilder.h"
#include "llvm/Passes/PassPlugin.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/IRBuilder.h"

using namespace llvm;

namespace {

struct SkeletonPass : public PassInfoMixin<SkeletonPass> {
    PreservedAnalyses run(Module &M, ModuleAnalysisManager &AM) {
        for (auto &F : M) {
            errs() << "I saw a function called " << F.getName() << "!\n";
            for (auto &B : F) {
              errs() << "Basic Block.\n";
              for (auto &I : B) {
                errs() << "Instruction: " << I << "\n";
                
                if(auto *op = dyn_cast<BinaryOperator>(&I)) {
                  /* errs() << "binary operator\n"; */
                  IRBuilder<> builder(op);

                  Value *lhs = op->getOperand(0);
                  Value *rhs = op->getOperand(1);
                  Value *mul = builder.CreateMul(lhs, rhs);

                  for (auto &U : op->uses()) {
                    User *user = U.getUser();
                    user->setOperand(U.getOperandNo(), mul);
                  }
                }
              }
            }
        }
        return PreservedAnalyses::none();
    };
};

}

extern "C" LLVM_ATTRIBUTE_WEAK ::llvm::PassPluginLibraryInfo
llvmGetPassPluginInfo() {
    return {
        .APIVersion = LLVM_PLUGIN_API_VERSION,
        .PluginName = "Skeleton pass",
        .PluginVersion = "v0.1",
        .RegisterPassBuilderCallbacks = [](PassBuilder &PB) {
            PB.registerPipelineStartEPCallback(
                [](ModulePassManager &MPM, OptimizationLevel Level) {
                    MPM.addPass(SkeletonPass());
                });
        }
    };
}
