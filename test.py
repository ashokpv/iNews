# Function to convert the matrix
def convert(mat, row, seats_book):
    (M, N) = (len(mat), len(mat[0]))
    print(M)
    print(N)
    rowFlag = colFlag = False
    # scan first row for any 0's
    # mat[4]
    # for j in range(N):
    #     if mat[0][j] == 0:
    #         rowFlag = True
    #         break

    # scan first column for any 0'ss
    for i in seats_book:
        if mat[row][i] == 0:
            mat[row][i] = 1
            # break

    # process rest of the matrix and use first row &
    # first column to mark if any cell in corresponding
    # # row or column has value 0 or not
    # for i in range(1, M):
    #     for j in range(1, N):
    #         if mat[i][j] == 0:
    #             mat[0][j] = mat[i][0] = 0
    #
    # # if (0, j) or (i, 0) is 0, assign 0 to cell (i, j)
    # for i in range(1, M):
    #     for j in range(1, N):
    #         if mat[0][j] == 0 or mat[i][0] == 0:
    #             mat[i][j] = 0
    #
    # # if rowFlag is True, then assign 0 to all cells of first row
    # i = 0
    # while rowFlag and i < N:
    #     mat[0][i] = 0
    #     i = i + 1
    #
    # # if colFlag is True, then assign 0 to all cells of first column
    # i = 0
    # while colFlag and i < M:
    #     mat[i][0] = 0
    #     i = i + 1


if __name__ == '__main__':

    mat = [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0]
    ]

    # convert the matrix
    convert(mat,3,[1,3])

    for r in mat:
        print(r)
