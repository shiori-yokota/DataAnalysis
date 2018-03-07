print("***Start Naive Bayes***")
library(dplyr)
library(e1071) # NaiveBayes

#***********************###### IMPORT DATA ######***********************#

recipe_raw <- read.csv("../../db/MixedDB.csv", stringsAsFactors=F, header=T, row.names=1)

recipe_raw$道具名  <- factor(recipe_raw$道具名)
recipe_raw$動作id2 <- factor(recipe_raw$動作id2)
table(recipe_raw$道具名)
table(recipe_raw$動作id2)
tool.labels <- recipe_raw$道具名
#head(recipe_raw)

# make materials
text <- paste(recipe_raw$X1, recipe_raw$X2, recipe_raw$X3, recipe_raw$X4, recipe_raw$X5, recipe_raw$X6, recipe_raw$X7, recipe_raw$X8)
recipe_raw           <- transform(recipe_raw, Materials=text)
recipe_raw$Materials <- as.character(recipe_raw$Materials)
# str(recipe_raw)

Term.All <- unlist(strsplit(text, " "))
Term.All <- Term.All[Term.All != ""]
Term.material <- as.data.frame(Term.All)
Term.material <- as.character(Term.material[!duplicated(Term.material$Term.All), ])

recipeDB <- recipe_raw[, c(15,12,14)]
out      <- c(115,127,128,131,208,222,274,279,285,359)

testNum  <- c(
  12,61,74,137,154,191,194,197,200,220,226,248,271,280,310,318,327,351,366,408
)
withoutTrainNum <- append(out, testNum)

#***********************###### FUNCTION() ######***********************#

myNaiveBayes <- function(x, y) {
  lev <- levels(y)
  #term frequency in each category
  ctf <- sapply(lev, function(label) {
    colSums(x[y==label, ])
  }) ## same python
#  term propability in each category smoothed using Laplace smoothing : p(material | tool)
#  ctp <- t(t(ctf + 1) / (colSums(ctf) + nrow(ctf)))
  #term propability in each category : p(material | tool)
  ctp <- t(t(ctf) / colSums(ctf)) ## wrong python
  #print(t(ctf))
  #print(colSums(ctf))
  #print(ctp)
  #number of each class documents
  nc <- table(y, dnn=NULL)
  #class prior : p(tool) or p(tool, motion)
  cp <- nc / sum(nc)
  structure(list(lev = lev, cp = cp, ctp = ctp), class="myNaiveBayes")
}

predict.myNaiveBayes <- function(model, x) {
#  prob <- apply(x, 1, function(x) {
#    colSums(log(model$ctp) * x)
#  })
#  prob <- prob + log(as.numeric(model$cp))
#  print(prob)
#  level <- apply(prob, 2, which.max)
#  model$lev[level]
  
  prob <- apply(x, 1, function(row) {
    tmp <- model$ctp * row # matrix p(x_i|t)
    t <- c()
    for(i in 1:nrow(as.matrix(row))) {
      if(as.matrix(row)[i] != 0) {
        t <- rbind(t, tmp[i, ])
      }
    }
    #print(t)
    t <- apply(t, 2, function(col) {
      prod(col)
    })
    #print(t)
    return(t) 
  }) # matrix p(x_1|t)p(x_2|t)...
  prob <- prob * as.numeric(model$cp) # matrix p(t)p(x_1|t)p(x_2|t)...
  # print(prob)
  # print(colSums(prob))
  prob <- t(t(prob) / colSums(prob))
  # print(prob)
  level <- apply(prob, 2, which.max)
  model$lev[level]
}

myTable <- function(x, y) {
  lev = levels(y)
  tbl <- matrix(0, nrow=length(lev), ncol=length(lev))
  colnames(tbl) <- lev
  rownames(tbl) <- lev
  for (i in 1:length(y)) {
    tbl[x[i], y[i]] <- tbl[x[i], y[i]] + 1
  }
  return(tbl)
} 

#***********************###### DIFINITION : ESTIMATE TOOL ######***********************#

material_dtm <- matrix(0, nrow=nrow(recipeDB), ncol=length(Term.material))
colnames(material_dtm) <- Term.material
for(i in 1:nrow(recipeDB)) {
  sentence <- recipeDB[i,1]
  sentence <- unlist(strsplit(sentence, " "))
  sentence <- sentence[sentence != ""]
  for(j in 1:length(sentence)) {
    material_dtm[i,sentence[j]] <- material_dtm[i,sentence[j]] + 1
  }
}

data.test.tool         <- material_dtm[testNum, ]
data.test.tool.label   <- recipeDB[testNum, "道具名"]
data.train.tool         <- material_dtm[-withoutTrainNum, ]
data.train.tool.label   <- recipeDB[-withoutTrainNum, "道具名"]

#***********************###### CODE : ESTIMATE TOOL ######***********************#
print("material -> tool")

model.tool <- myNaiveBayes(data.train.tool, data.train.tool.label)
pred.tool  <- predict(model.tool, data.test.tool)
print(pred.tool)
predmat.tool <- matrix(pred.tool)

write(predmat.tool, file="../../result/bestToolName.txt")

table.tool <- myTable(pred.tool, data.test.tool.label)
# print(table)
print(sum(diag(table.tool)))
print(sum(diag(table.tool)) / length(data.test.tool.label)) # A rate of correct answer

#***********************###### CODE : ESTIMATE MOTION ######***********************#

material_tool_dtm <- matrix(0, nrow=nrow(recipeDB), ncol=length(levels(tool.labels)))
colnames(material_tool_dtm) <- levels(tool.labels)
for(i in 1:nrow(recipeDB)) {
  tool <- recipeDB[i, 2]
  material_tool_dtm[i, tool] <- material_tool_dtm[i, tool] + 1
}
material_tool_dtm <- cbind(material_dtm, material_tool_dtm)

estimate_tool_dtm <- matrix(0, nrow=nrow(predmat.tool), ncol=length(levels(tool.labels)))
colnames(estimate_tool_dtm) <- levels(tool.labels)
for(i in 1:nrow(predmat.tool)) {
  tool <- predmat.tool[i]
  estimate_tool_dtm[i, tool] <- estimate_tool_dtm[i, tool] + 1
}

data.test.motion        <- cbind(data.test.tool, estimate_tool_dtm)
data.test.motion.label  <- recipeDB[testNum, "動作id2"]
data.train.motion       <- material_tool_dtm[-withoutTrainNum, ]
data.train.motion.label <- recipeDB[-withoutTrainNum, "動作id2"]

#***********************###### CODE : ESTIMATE MOTION ######***********************#
print("material -> motion")

model.motion <- myNaiveBayes(data.train.motion, data.train.motion.label)
pred.motion  <- predict(model.motion, data.test.motion)
print(pred.motion)
predmat.motion <- matrix(pred.motion)

write(predmat.motion, file="../../result/bestMotionID.txt")

table.motion <- myTable(pred.motion, data.test.motion.label)
# print(table)
print(sum(diag(table.motion)))
print(sum(diag(table.motion)) / length(data.test.motion.label)) # A rate of correct answer
